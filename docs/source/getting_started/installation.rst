=========================================================
Django Sage OTP and User Authentication Configuration
=========================================================

Overview
========
This documentation covers the configuration and usage of Django Sage's OTP (One-Time Password) and User Authentication management.

Installation
============
To install the `sage_auth` and `sage_otp` modules for managing OTPs and custom user authentication, follow these steps:

1. Install the required dependencies using `pip`:

   .. code-block:: bash

      pip install django-sage-auth django-sage-otp

2. Add the required apps to your Django settings:

   .. code-block:: python

      INSTALLED_APPS = [
          # other apps
          "sage_auth",
          "sage_otp",
          "phonenumber_field",
      ]

3. Apply migrations:

   .. code-block:: bash

      python manage.py makemigrations
      python manage.py migrate


Configuration
=============
To use `sage_auth` and `sage_otp`, you need to add specific configurations in your Django `settings.py`. Below are the available settings:

OTP Settings
------------
You can control how OTP verifications and lockouts behave using the following settings:

- **OTP_LOCKOUT_DURATION**: Defines how long (in minutes) a user is locked out after exceeding the number of allowed OTP attempts.

  .. code-block:: python

     OTP_LOCKOUT_DURATION = 3  # In minutes

- **OTP_MAX_FAILED_ATTEMPTS**: Specifies the number of times a user can enter an incorrect OTP before the account is temporarily locked.

  .. code-block:: python

     OTP_MAX_FAILED_ATTEMPTS = 4

- **OTP_MAX_REQUEST_TIMEOUT**: Defines how many OTP verification requests are allowed before a user is locked out temporarily.

  .. code-block:: python

     OTP_MAX_REQUEST_TIMEOUT = 10

- **OTP_BLOCK_COUNT**: Defines how many time after use is set to wait will be block

  .. code-block:: python

     OTP_BLOCK_COUNT = 10

- **ACTIVATION_LINK_EXPIRY_MINUTES**: Define How many time the activates link is valid

  .. code-block:: python

     ACTIVATION_LINK_EXPIRY_MINUTES = 1

Authentication Methods
----------------------
You can configure how users authenticate with your system. Choose whether users authenticate using email, phone number, or username:

.. code-block:: python

   AUTHENTICATION_METHODS = {
       "EMAIL_PASSWORD": True,  # Enable email authentication
       "PHONE_PASSWORD": True,  # Enable phone number authentication
       "USERNAME_PASSWORD": False,  # Disable username authentication
   }

.. note::

   The first method listed as `True` in the `AUTHENTICATION_METHODS` setting is used as the primary identifier for the user. For example, if `EMAIL_PASSWORD` is set to `True`, the user's email will be used as the primary identifier.

When using phone number authentication, ensure that the `phonenumber_field` package is installed and configured to validate and format phone numbers correctly.

Optional Settings
-----------------
1. **SEND_OTP**: This setting controls whether OTPs are sent to users. If `SEND_OTP` is set to `False`, no OTPs will be sent.

   .. code-block:: python

      SEND_OTP = False

2. **USER_ACCOUNT_ACTIVATION_ENABLED**: This setting enables user account activation. When set to `True`, an activation link will be sent to the user’s email.

   .. code-block:: python

      USER_ACCOUNT_ACTIVATION_ENABLED = True

3. **COMPANY_EMAIL_DOMAINS**: You can restrict user registration to specific email domains by configuring this setting. For example, setting this to `sageteam.org` ensures that only users with this email domain can register.

   .. code-block:: python

      COMPANY_EMAIL_DOMAINS = ["sageteam.org"]

Email OTP Configuration
------------------------
To send OTPs via email, configure your email backend in `settings.py`:

.. code-block:: python

   EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
   EMAIL_HOST = "smtp.gmail.com"
   EMAIL_PORT = 587
   EMAIL_HOST_USER = "your-email@gmail.com"
   EMAIL_HOST_PASSWORD = "your-email-password"
   EMAIL_USE_TLS = True
   DEFAULT_FROM_EMAIL = "Your Company <your-email@gmail.com>"

You can adjust the email settings to match your email provider.

SMS OTP Configuration
----------------------
For SMS-based OTPs, you'll need to set up an SMS provider in your settings. Here's an example configuration for the SMS service provider:

.. code-block:: python

   SMS_CONFIGS = {
       "debug": True,
       "provider": {
           "NAME": "sms.ir",  # The name of your SMS provider
           "API_KEY": "your-api-key-here",  # Replace with your SMS API key
       },
   }

This configuration allows your application to send OTPs via the SMS provider specified.

Custom User Model
=================
You need to define the custom user model in your Django settings file. Make sure the following line is added:

.. code-block:: python

   AUTH_USER_MODEL = "sage_auth.SageUser"

This will point to the custom user model provided by `sage_auth`, which supports email, phone, and username-based authentication.

One-Time Password (OTP) Workflow
================================
The `sage_auth` module manages OTP verification with customizable behaviors. Here's an overview of its workflow:

1. **OTP Generation and Sending**:
   
   - When a user registers or requests to verify their account, an OTP is generated.
   - The OTP can be sent via email or SMS depending on the authentication method.

2. **OTP Verification**:

   
   - The user enters the OTP received via email or SMS.
   - The system checks if the OTP matches, verifies it, and activates the account.

3. **Handling OTP Expiration**:
   
   - If the OTP expires or the user exceeds the maximum number of failed attempts, the system locks the user temporarily and sends a new OTP.
