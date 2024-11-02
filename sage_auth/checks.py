from django.conf import settings
from django.core.checks import Error, register


@register()
def check_authentication_methods(app_configs, **kwargs):
    errors = []

    if not hasattr(settings, "AUTHENTICATION_METHODS") or not isinstance(
        settings.AUTHENTICATION_METHODS, dict
    ):
        errors.append(
            Error(
                "'AUTHENTICATION_METHODS' setting is missing or is not a dictionary.",
                hint="Define 'AUTHENTICATION_METHODS' in your settings as a dictionary.",
                obj=settings,
                id="authentication.E000",
            )
        )
        return errors

    if not settings.AUTHENTICATION_METHODS.get(
        "EMAIL_PASSWORD", False
    ) and not settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD", False):
        errors.append(
            Error(
                "Either 'EMAIL_PASSWORD' or 'PHONE_PASSWORD' must be enabled in 'AUTHENTICATION_METHODS'.",
                hint="Enable at least one of 'EMAIL_PASSWORD' or 'PHONE_PASSWORD' in 'AUTHENTICATION_METHODS'.",
                obj=settings,
                id="authentication.E001",
            )
        )
    if getattr(
        settings, "USER_ACCOUNT_ACTIVATION_ENABLED", False
    ) and not settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD", False):
        errors.append(
            Error(
                "'USER_ACCOUNT_ACTIVATION_ENABLED' is set to True, but 'EMAIL_PASSWORD' is not enabled.",
                hint="Enable 'EMAIL_PASSWORD' in 'AUTHENTICATION_METHODS' when 'USER_ACCOUNT_ACTIVATION_ENABLED' is True.",
                obj=settings,
                id="authentication.E002",
            )
        )
    if getattr(settings, "SEND_OTP", False) and getattr(
        settings, "USER_ACCOUNT_ACTIVATION_ENABLED", False
    ):
        errors.append(
            Error(
                "Both 'SEND_OTP' and 'USER_ACCOUNT_ACTIVATION_ENABLED' cannot be True at the same time.",
                hint="Set either 'SEND_OTP' or 'USER_ACCOUNT_ACTIVATION_ENABLED' to False.",
                obj=settings,
                id="authentication.E003",
            )
        )
    return errors


@register()
def check_auth_user(app_configs, **kwargs):
    errors = []
    if not hasattr(settings, "AUTH_USER_MODEL"):
        errors.append(
            Error(
                "'AUTH_USER_MODEL' setting is missing.",
                hint="Define 'AUTH_USER_MODEL' in your settings to specify a sage_auth user model.",
                obj=settings,
                id="authentication.E003",
            )
        )
    return errors


@register()
def check_email_settings(app_configs, **kwargs):
    errors = []
    if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD", False):
        required_email_settings = [
            "EMAIL_BACKEND",
            "EMAIL_HOST",
            "EMAIL_HOST_USER",
            "EMAIL_PORT",
            "EMAIL_USE_TLS",
            "DEFAULT_FROM_EMAIL",
        ]

        for setting in required_email_settings:
            if not hasattr(settings, setting):
                errors.append(
                    Error(
                        f"'{setting}' is not set for 'EMAIL_PASSWORD'.",
                        hint=f"Set '{setting}' in your settings.",
                        obj=settings,
                        id=f"authentication.E00{required_email_settings.index(setting) + 2}",
                    )
                )

        if not getattr(settings, "EMAIL_HOST_PASSWORD", None):
            errors.append(
                Error(
                    "'EMAIL_HOST_PASSWORD' is missing in your settings.",
                    hint="Set 'EMAIL_HOST_PASSWORD' in your settings.",
                    obj=settings,
                    id="authentication.E010",
                )
            )
    return errors


@register()
def check_sms_settings(app_configs, **kwargs):
    errors = []
    if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD", False):
        sms_configs = getattr(settings, "SMS_CONFIGS", None)
        if sms_configs is None or not isinstance(sms_configs, dict):
            errors.append(
                Error(
                    "'SMS_CONFIGS' is not set or is improperly configured for 'PHONE_PASSWORD'.",
                    hint="Ensure 'SMS_CONFIGS' is set as a dictionary with appropriate keys.",
                    obj=settings,
                    id="authentication.E011",
                )
            )
        else:
            provider = sms_configs.get("provider", {})
            api_key = provider.get("API_KEY")

            if not api_key:
                errors.append(
                    Error(
                        "'API_KEY' is missing in 'SMS_CONFIGS'.",
                        hint="Ensure 'API_KEY' is set in 'SMS_CONFIGS' provider settings.",
                        obj=settings,
                        id="authentication.E012",
                    )
                )

    return errors
