from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailVerificationBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        """Authenticates a user using their email and password.

        The authentication is done using the email field. If the email has been
        verified, the user is authenticated with the given password.

        Args:
            request: The current request object.
            email: The email address to authenticate.
            password: The password to authenticate.

        Returns:
            The authenticated user if the email has been verified and the
            password is correct, otherwise None.
        """
        UserModel = get_user_model()

        try:
            # Authenticate using the email field
            user = UserModel.objects.get(email=email)

            if user.email_verified:
                # Check the password if
                # the email has been verified
                if user.check_password(password):
                    return user
            else:
                # Return None if the email has not been verified
                return None
        except UserModel.DoesNotExist:
            # Return None if the user does not exist
            return None

    def user_can_authenticate(self, user):
        """Override to add email verification logic."""
        is_active = super().user_can_authenticate(user)
        return is_active and user.email_verified
