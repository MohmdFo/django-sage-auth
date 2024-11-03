from django.conf import settings
from sage_sms.factory import SMSBackendFactory

def get_backends():
    """
    Initializes and returns an SMS provider instance using the configured 
    backend from `settings.SMS_CONFIGS`.
    This function leverages the `SMSBackendFactory` to dynamically select and 
    initialize an SMS provider backend as specified in the Django settings.The 
    SMS provider can then be used to send messages based on application needs.
    """
    factory = SMSBackendFactory(settings.SMS_CONFIGS, "sage_auth.backends")
    sms_provider_class = factory.get_backend()
    sms_provider = sms_provider_class(settings)
    return sms_provider
