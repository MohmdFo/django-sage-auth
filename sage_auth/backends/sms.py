try:
    from sms_ir import SmsIr as SmsIRLib
except ImportError:
    SmsIRLib = None

from sage_sms.design.interfaces.provider import ISmsProvider
from sage_sms.validators import PhoneNumberValidator

class SmsIr(ISmsProvider):
    def __init__(self, settings):
        if SmsIRLib is None:
            raise ImportError("Install `smsir`, Run `pip install smsir`.")

        self.phone_number_validator = PhoneNumberValidator()
        self._api_key = settings["provider"]["API_KEY"]
        self._line_number = settings["provider"].get("LINE_NUMBER")
        self.smsir = SmsIRLib(self._api_key)

    def send_one_message(self, phone_number: str, message: str, linenumber=None) -> None:
        cast_phone_number = self.phone_number_validator.validate_and_format(phone_number, region="IR")
        self.smsir.send_sms(cast_phone_number, message, self._line_number)

    def send_bulk_messages(self, phone_numbers: list[str], message: str, linenumber=None) -> None:
        raise NotImplementedError

    def send_verify_message(self, phone_number: str, value: str) -> None:
        raise NotImplementedError