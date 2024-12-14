from django.dispatch import Signal

# Define custom signals
user_login_attempt = Signal(providing_args=["user", "identifier", "success"])
user_login_failed = Signal(providing_args=["identifier"])
