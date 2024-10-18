Mixins Overview
===============

This documentation provides an overview of the various mixins included in this package. These mixins are designed to streamline and modularize the processes of user authentication, OTP (One-Time Password) validation, password management, and account reactivation.

Mixins Descriptions
===================

ForgetPasswordMixin
-------------------

**Purpose**: 
Handles the initiation of the password reset process by sending an OTP to the user's registered email or phone number when they request a password reset.

**Key Features**:
   - Sends an OTP to the user’s email or phone number when they request a password reset.
   - Ensures that only valid requests trigger OTP generation.

ForgetPasswordConfirmMixin
--------------------------

**Purpose**:
This mixin verifies the OTP provided by the user during the password reset process.

**Key Features**:
   - Verifies the OTP provided by the user.
   - Ensures OTP validity and expiry times are respected.


ForgetPasswordDoneMixin
-----------------------

**Purpose**:
Completes the password reset process. Once the OTP is verified, this mixin allows the user to set a new password.

**Key Features**:
   - Handles OTP verification success and provides the interface for password reset.
   - Supports password complexity validation.

VerifyOtpMixin
--------------

**Purpose**:
Verifies the OTP provided by the user during processes such as signup, reactivation, or other OTP-based authentication flows.

**Key Features**:
   - Validates OTP and activates the user's account upon successful verification.
   - Supports OTP expiry and failure handling.


ReactivationMixin
-----------------

**Purpose**:
Manages account reactivation requests by sending a new OTP or activation link to users whose accounts are inactive.

**Key Features**:
   - Sends a new OTP or activation email to re-enable accounts.
   - Checks for existing active OTPs before generating new ones.


SignupMixin
-----------

**Purpose**:
Handles the user signup process, which includes creating a new account, sending OTPs for verification, and activating the account.

**Key Features**:
   - Creates a new user account.
   - Sends OTP to email or phone for account verification.


PasswordResetMixin
------------------

**Purpose**:
Facilitates password reset for users who have forgotten their passwords. It includes an OTP verification step for security.

**Key Features**:
   - Allows users to reset passwords after verifying an OTP.
   - Ensures password meets validation requirements.

ReactivateAccountMixin
----------------------

**Purpose**:
Helps users reactivate their inactive accounts by generating a new OTP or sending an account activation link.

**Key Features**:
   - Sends a new OTP or activation link for account reactivation.
   - Handles activation through OTP verification.

**Relevant Settings**:
   - `USER_ACCOUNT_ACTIVATION_ENABLED`: Enable/disable the reactivation process.
   - `SEND_OTP`: Set to `True` to use OTP for account reactivation.

OTPValidationMixin
------------------

**Purpose**:
Provides a mechanism for validating OTPs at any step of the authentication or recovery process.

**Key Features**:
   - Verifies OTP tokens and handles related errors.
   - Ensures OTP validity before proceeding with authentication.

**Relevant Settings**:
   - `OTP_EXPIRE_TIME`: Defines the time window in seconds during which an OTP remains valid.
   - `OTP_MAX_FAILED_ATTEMPTS`: Set to limit how many failed OTP attempts are allowed.

LoginMixin
----------

**Purpose**:
Manages the login process by verifying the user's credentials. Supports login via email, phone number, or username based on system settings.

**Key Features**:
   - Validates user login credentials.
   - Supports multiple authentication methods (email, phone number, or username).

PasswordChangeMixin
-------------------

**Purpose**:
Allows logged-in users to change their password.

**Key Features**:
   - Provides password change functionality for authenticated users.
   - Enforces password validation rules.


.. admonition:: Real-Life Example

   For a practical implementation of these mixins, including how to configure views and settings in a Django project, please visit the following GitHub repository:

   - [GitHub Repository: Real-life Example](https://github.com/radinceorc/sage_auth_example)