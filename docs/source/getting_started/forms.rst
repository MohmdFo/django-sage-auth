Forms Overview
==============

This section covers the mixin-based forms included in the package. These forms are designed to be dynamic and flexible, depending on the authentication strategies set in the system. Each form handles key parts of user management, such as user creation, password reset, and OTP login.

Forms Descriptions
==================

SageUserFormMixin
-----------------

**Purpose**:
This is a base form mixin used to dynamically generate fields for user creation based on the authentication strategies defined in the system. It supports email, phone number, and username as identifiers.

**Key Features**:
   - Dynamically generates fields like email, phone number, or username.
   - Validates user passwords using Django’s built-in password validators.
   - Ensures that at least one identifier (email, phone number, or username) is provided.
   - Handles password confirmation to ensure both password fields match.

SageUserCreationForm
--------------------

**Purpose**:
This form extends `SageUserFormMixin` to handle the user creation process.

**Key Features**:
   - Provides fields for email, phone number, or username.
   - Includes password fields (`password1` and `password2`) to handle password input and confirmation.
   - Applies validation rules for passwords and identifier fields.

PasswordResetFormMixin
----------------------

**Purpose**:
This mixin handles password reset requests by dynamically generating the appropriate identifier field based on the authentication method (email, phone number, or username).

**Key Features**:
   - Dynamically generates a field for email or phone number based on system configuration.
   - Ensures that a valid identifier is provided for the password reset process.

OtpLoginFormMixin
-----------------

**Purpose**:
This mixin is designed to handle login processes that rely on OTP (One-Time Password) authentication. It dynamically creates a field for the identifier (email, phone number, or username).

**Key Features**:
   - Dynamically creates a field for login using email or phone number.
   - Supports flexible identifier types.

PasswordResetForm
-----------------

**Purpose**:
This form extends `PasswordResetFormMixin` to handle the initial step in the password reset process, allowing the user to input their identifier (email or phone number).

**Key Features**:
   - Provides a form for the user to input their email or phone number to request a password reset.
   - Supports both email and phone number.

ResetPasswordConfirmForm
------------------------

**Purpose**:
This form handles the final step in the password reset process, allowing users to enter and confirm a new password after OTP verification.

**Key Features**:
   - Allows the user to input and confirm a new password.
   - Ensures that the new password adheres to validation rules.
   - Automatically applies the password confirmation logic.

.. admonition:: Real-Life Example

   For a practical implementation of these forms and how to integrate them into your project, please visit the following GitHub repository:

   - [GitHub Repository: Real-life Example](https://github.com/radinceorc/sage_auth_example)
