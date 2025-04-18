"""Manages sending emails to users pertaining to their accounts."""

import logging

from django.urls import reverse
from django.utils import encoding, http

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class EmailManager:
    sender = settings.DEFAULT_FROM_EMAIL

    def send(self, subject, message, html_message, recipient_list):
        logger.info("Sending email to %s", recipient_list)
        send_mail(
            subject, message, self.sender, recipient_list, html_message=html_message
        )


class UserEmailManager(EmailManager):
    """Manages sending emails to users pertaining to their accounts.

    AccountsEmailManager inherits from EmailManager and provides a centralised point for
    sending emails which pertain to a users account.
    """

    def __init__(self):  # noqa: D107
        super().__init__()

    def mail_verification(self, request, user):
        """Sends an email to the user with a verification link to confirm their email.

        Args:
            request (`django.http.HttpRequest`): The HTTP request object, used to build
            the absolute URI for the verification link.
            user (`django.contrib.auth.models.User`): The user object for whom the email
            verification link is being generated.

        The email contains a token-based verification URL which
        when clicked will verify the user's email address.
        """
        # Generate verification token
        from .tokens import email_verification_token

        token = email_verification_token.make_token(user)

        # Build verification URL
        verification_url = request.build_absolute_uri(
            reverse(
                "users:verify_email", kwargs={"user_id": user.id, "token": token}
            )
        )

        # Send email
        subject = "Verify your email"
        message = f"Please click the link to verify your email: {verification_url}"
        html_message = (
            f"<p>Please click the link to verify your email: {verification_url}</p>"
        )
        recipient = [user.email]
        self.send(subject, message, html_message, recipient)

    def mail_password_reset(self, request, user):
        """Sends an email to the user with a link to reset their password.

        Args:
            request (`django.http.HttpRequest`): The HTTP request object, used to build
            the absolute URI for the password reset link.
            user (`django.contrib.auth.models.User`): The user object for whom the
            password reset link is being generated.

        The email contains a token-based verification URL which
        when clicked will allow the user to reset their password.
        """
        from .tokens import password_reset_token

        token = password_reset_token.make_token(user)

        # Build password reset URL
        password_reset_url = request.build_absolute_uri(
            reverse(
                "users:password_reset_confirm",
                kwargs={
                    "uidb64": http.urlsafe_base64_encode(encoding.force_bytes(user.pk)),
                    "token": token,
                },
            )
        )

        # Send email
        subject = "Reset your password"
        message = f"Please click the link to reset your password: {password_reset_url}"
        html_message = (
            f"<p>Please click the link to reset your password: {password_reset_url}</p>"
        )
        recipient = [user.email]
        self.send(subject, message, html_message, recipient)
