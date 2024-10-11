# Django Sage Auth
Django Sage Auth is a Django application designed for handling user authentication, including OTP-based (One-Time Password) verification, account activation via email or phone, and password reset functionality. It provides a flexible system for implementing various authentication strategies, including email, phone number, and username-based login.

## Features

- Support for multiple authentication methods: email, phone number, and username.
- OTP-based user verification for secure authentication.
- Account activation via email links or OTPs.
- Password reset via email, with support for secure token generation.
- User management with customizable authentication strategies.
- Easy integration with Django's authentication system.

## Installation

### Using `pip` with `virtualenv`

1. **Create a Virtual Environment**:

    ```bash
    python -m venv .venv
    ```

2. **Activate the Virtual Environment**:

   - On Windows:

     ```bash
     .venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

3. **Install `django-sage-auth`**:

    ```bash
    pip install django-sage-auth
    ```

### Using `poetry`

1. **Initialize Poetry** (if not already initialized):

    ```bash
    poetry init
    ```

2. **Install `django-sage-auth`**:

    ```bash
    poetry add django-sage-auth
    ```

3. **Apply Migrations**:

    After installation, make sure to run the following commands to create the necessary database tables:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## Configuration

### Django Settings

Add `django-sage-auth` to your `INSTALLED_APPS` in the Django settings and configure the authentication methods and OTP settings:

```python
INSTALLED_APPS = [
    # other packages
    "sage_auth",
]

# Configure the authentication methods
AUTHENTICATION_METHODS = {
    "EMAIL_PASSWORD": True,
    "PHONE_PASSWORD": True,
    "USERNAME_PASSWORD": True,
}

# Configure the OTP settings
OTP_LOCKOUT_DURATION = 3  # in minutes
OTP_MAX_FAILED_ATTEMPTS = 4
```

### URL Configuration

Add the URL patterns for Django Sage Auth to your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('auth/', include('sage_auth.urls')),
    # other paths
]
```

## Usage

### Account Activation

To activate an account via email:

1. Register a user with an inactive account.
2. The user receives an email with an activation link or OTP.
3. The user follows the link or enters the OTP to activate their account.

### OTP Verification

To verify a user using OTP:

1. Generate an OTP for the user via email or SMS.
2. The user enters the OTP on the verification page.
3. If the OTP is valid, the user's account is activated.

### Password Reset

To reset a user's password:

1. The user requests a password reset.
2. An email with a password reset link is sent to the user.
3. The user follows the link and sets a new password.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please follow the guidelines in the `CONTRIBUTING.md` file when submitting a pull request.

## Support

For support, please open an issue on the GitHub repository.
