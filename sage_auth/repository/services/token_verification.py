# services/otp_verification_service.py

import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone as tz

from sage_otp.models import OTP
from sage_otp.repository.managers.otp import OTPManager
from sage_otp.helpers.choices import OTPState, ReasonOptions

from sage_auth.models import SageUser
from sage_auth.utils import get_backends, send_email_otp
from sage_auth.signals import otp_expired, otp_failed, otp_verified

logger = logging.getLogger(__name__)


class OTPVerificationService:
    """
    A service for managing OTP verification and related user account operations.

    This service handles the core logic for validating One-Time Passwords (OTPs) used
    in user authentication and account recovery workflows. It provides methods to verify
    OTPs, manage OTP expiration, send new OTPs, and block users in case of repeated failed
    attempts. The class encapsulates all OTP-related business logic, ensuring that the
    view layer remains clean and focused on HTTP-specific concerns.

    This service is essential for ensuring secure and user-friendly authentication mechanisms.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object from the view, used for accessing session and request-related data.
    user_identifier : str
        A unique identifier for the user, such as an email address or phone number.
    reason : str
        The reason for OTP verification, typically one of the options from `ReasonOptions`.

    Attributes
    ----------
    request : HttpRequest
        The HTTP request object passed during initialization.
    user_identifier : str
        The unique identifier for the user (email or phone).
    reason : str
        The reason for OTP verification.
    otp_manager : OTPManager
        A helper object for managing OTP-related operations in the database.

    Notes
    -----
    - This class interacts with models like `SageUser` and `OTP`, as well as external utilities
      for sending OTPs via email or SMS.
    - Signal handlers (`otp_verified`, `otp_failed`, `otp_expired`) are triggered during OTP processing.

    Examples
    --------
    >>> service = OTPVerificationService(request, "user@example.com", ReasonOptions.EMAIL_ACTIVATION)
    >>> user = service.get_user_by_identifier()
    >>> result = service.verify_otp(user, "123456")
    >>> if result["success"]:
    >>>     print("OTP verified successfully!")
    """
    def __init__(self, request, user_identifier, reason):
        self.request = request
        self.user_identifier = user_identifier
        self.reason = reason
        self.otp_manager = OTPManager()

    def get_user_by_identifier(self):
        """
        Retrieves a user from the database based on their unique identifier.

        This method fetches a `SageUser` object using either the email address
        or phone number provided as the `user_identifier`. It returns `None` if
        no user matches the identifier.

        Returns
        -------
        SageUser or None
            The user object if a matching user is found; otherwise, `None`.

        Notes
        -----
        - This method assumes that the `user_identifier` is either an email or
          phone number. The format of the identifier should be validated before
          calling this method.
        - Handles `SageUser.DoesNotExist` gracefully and logs the occurrence.

        Examples
        --------
        >>> service = OTPVerificationService(request, "user@example.com", ReasonOptions.EMAIL_ACTIVATION)
        >>> user = service.get_user_by_identifier()
        >>> if user:
        >>>     print(f"User found: {user.id}")
        >>> else:
        >>>     print("No user found.")
        """
        try:
            logger.debug("Attempting to retrieve user by identifier: %s", self.user_identifier)
            if "@" in self.user_identifier:
                user = SageUser.objects.get(email=self.user_identifier)
            else:
                user = SageUser.objects.get(phone_number=self.user_identifier)
            logger.info("User retrieved successfully: User ID %s", user.id)
            return user
        except SageUser.DoesNotExist:
            logger.warning("User not found for identifier: %s", self.user_identifier)
            return None

    def verify_otp(self, user, entered_otp):
        try:
            logger.debug("Verifying OTP for user ID: %s", user.id)
            otp_instance = self.otp_manager.get_otp(identifier=user.id, reason=self.reason)

            otp_max_attempts = getattr(settings, "OTP_MAX_FAILED_ATTEMPTS", 4)
            otp_expiry_time = otp_instance.last_sent_at + timedelta(
                seconds=self.otp_manager.EXPIRE_TIME.seconds
            )
            time_left_to_expire = (otp_expiry_time - tz.now()).total_seconds()

            if time_left_to_expire <= 0:
                logger.warning(
                    "OTP expired for user ID: %s. Sending new OTP.", user.id
                )
                otp_instance.update_state(OTPState.EXPIRED)
                otp_expired.send(sender=self.__class__, user=user, reason=self.reason)
                self.send_new_otp(user)
                return {"success": False, "status": "expired"}

            if otp_instance.failed_attempts_count >= otp_max_attempts:
                logger.warning(
                    "Maximum OTP attempts reached for user ID: %s. Sending new OTP.", user.id
                )
                otp_failed.send(
                    sender=self.__class__,
                    user=user,
                    reason=self.reason,
                    attempts=otp_instance.failed_attempts_count,
                )
                self.send_new_otp(user)
                return {"success": False, "status": "max_attempts"}

            if otp_instance.token == entered_otp:
                logger.info("OTP verified successfully for user ID: %s", user.id)
                otp_instance.state = OTPState.CONSUMED
                user.is_active = True
                user.save()
                otp_instance.save()
                otp_verified.send(sender=self.__class__, user=user, success=True, reason=self.reason)
                return {"success": True, "status": "verified", "user": user}
            else:
                otp_instance.failed_attempts_count += 1
                otp_instance.save()
                logger.warning(
                    "Incorrect OTP entered for user ID: %s. Failed attempts: %d",
                    user.id,
                    otp_instance.failed_attempts_count,
                )
                otp_failed.send(
                    sender=self.__class__,
                    user=user,
                    reason=self.reason,
                    attempts=otp_instance.failed_attempts_count,
                )
                return {"success": False, "status": "incorrect"}
        except OTP.DoesNotExist:
            logger.error("OTP instance not found for user ID: %s", user.id)
            return {"success": False, "status": "invalid"}
        except Exception as e:
            logger.critical(
                "Unexpected error during OTP verification for user ID: %s. Error: %s",
                user.id,
                str(e),
            )
            return {"success": False, "status": "error"}

    def send_new_otp(self, user):
        """
        Generates and sends a new OTP to the user's registered email or phone.

        Depending on the format of the `user_identifier`, this method sends the OTP
        via email or SMS. A new OTP is created or retrieved if it already exists.

        Parameters
        ----------
        user : SageUser
            The user object representing the recipient of the new OTP.

        Notes
        -----
        - For email-based identifiers, the OTP is sent via the `send_email_otp` utility.
        - For phone-based identifiers, the OTP is sent via SMS using the appropriate backend.

        Examples
        --------
        >>> service = OTPVerificationService(request, "user@example.com", ReasonOptions.EMAIL_ACTIVATION)
        >>> user = service.get_user_by_identifier()
        >>> service.send_new_otp(user)
        """
        try:
            if "@" in self.user_identifier:
                logger.debug("Generating new OTP for user ID: %s via email.", user.id)
                otp_data = self.otp_manager.get_or_create_otp(identifier=user.id, reason=self.reason)
                send_email_otp(otp_data[0].token, user.email)
                logger.info("New OTP sent via email to user ID: %s", user.id)
            else:
                logger.debug("Generating new OTP for user ID: %s via SMS.", user.id)
                otp_data = self.otp_manager.get_or_create_otp(identifier=user.id, reason=self.reason)
                sms_obj = get_backends()
                sms_obj.send_one_message(str(user.phone_number), otp_data[0].token)
                logger.info("New OTP sent via SMS to user ID: %s", user.id)
        except Exception as e:
            logger.error("Failed to send new OTP to user ID: %s. Error: %s", user.id, str(e))

    def block_user(self, user):
        """
        Blocks the user account and marks their OTP as expired.

        This method deactivates the user account and prevents further OTP attempts.
        All existing OTPs for the user are marked as expired to prevent misuse.

        Parameters
        ----------
        user : SageUser
            The user object representing the account to be blocked.

        Notes
        -----
        - The user's `is_block` and `is_active` flags are updated in the database.
        - This method should be invoked when a user exceeds the maximum allowed OTP attempts.

        Examples
        --------
        >>> service = OTPVerificationService(request, "user@example.com", ReasonOptions.EMAIL_ACTIVATION)
        >>> user = service.get_user_by_identifier()
        >>> service.block_user(user)
        """
        try:
            logger.warning("Blocking user ID: %s", user.id)
            user.is_block = True
            user.is_active = False
            user.save()

            otp_instance = self.otp_manager.get_otp(identifier=user.id, reason=self.reason)
            otp_instance.state = OTPState.EXPIRED
            otp_instance.save()
            logger.info("User ID %s successfully blocked and all OTPs expired.", user.id)
        except OTP.DoesNotExist:
            logger.error("Failed to retrieve OTP instance for blocking user ID: %s", user.id)
        except Exception as e:
            logger.critical("Error while blocking user ID: %s. Error: %s", user.id, str(e))
