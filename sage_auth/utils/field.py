from django.conf import settings

def set_required_fields():
    """
    Determines and sets the `USERNAME_FIELD` and `REQUIRED_FIELDS` for user 
    authentication based on enabled authentication methods in settings.

    This function inspects `settings.AUTHENTICATION_METHODS` to dynamically 
    select the primary identifier (`USERNAME_FIELD`) 
    and any additional required fields for user creation
    or login (e.g., email, phone number, username). 

    """
    if not any(settings.AUTHENTICATION_METHODS.values()):
        auth_methods = {
            "EMAIL_PASSWORD": True,
            "USERNAME_PASSWORD": True
        }
        settings.AUTHENTICATION_METHODS = auth_methods

    username_field = None
    required_fields = []

    for method in settings.AUTHENTICATION_METHODS:
        if settings.AUTHENTICATION_METHODS[method]:
            if username_field is None:
                if method == "EMAIL_PASSWORD":
                    username_field = "email"
                elif method == "PHONE_PASSWORD":
                    username_field = "phone_number"
                elif method == "USERNAME_PASSWORD":
                    username_field = "username"
            else:
                if method == "EMAIL_PASSWORD":
                    required_fields.append("email")
                elif method == "PHONE_PASSWORD":
                    required_fields.append("phone_number")
                elif method == "USERNAME_PASSWORD":
                    required_fields.append("username")

    required_fields = list(set(required_fields))
    return username_field, required_fields
