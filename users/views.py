
import logging

import datetime

from django import shortcuts, urls

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone


from . import forms, mail, utils
from .messages import UserMessageManager

logger = logging.getLogger("__name__")

User = auth.get_user_model()

email_manager = mail.UserEmailManager()

# users/views.py


def registration_type_view(request):

    if request.method == "POST":
        form = forms.RegistrationTypeForm(request.POST)
        if form.is_valid():
            account_type = form.cleaned_data.get('account_type')
            if account_type == "in":
                return shortcuts.redirect("users:individual-registration")
            elif account_type == "co":
                return shortcuts.redirect("users:organization-registration")
            else:
                shortcuts.render(request, "users/registration_type.html")
        else:
            print(f"FORM ERRORS: {form.errors}")
            messages.error(request, 'Invalid form submission.')
            return shortcuts.redirect('users:register')
    elif request.method == "GET":
        form = forms.RegistrationTypeForm()
        context = {"form": form}
        return shortcuts.render(request, "users/registration_type.html", context)


def individual_registration_view(request):

    if request.method == 'POST':
        user_form = forms.UserRegistrationForm(request.POST)
        profile_form = forms.IndividualProfileRegistrationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # Save user with individual role
            user = user_form.save(commit=False)
            user.role = 'individual'
            user.is_premium = False  # Default, can upgrade later
            user.save()
            # Save profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            # Email verification and messages
            messages.success(
                request, 'Account created! Verify your email.')
            email_manager.mail_verification(request, user)
            return shortcuts.redirect('users:login')

        # Handle form errors
        messages.error(request, 'Invalid form submission.')
        return shortcuts.redirect('users:register')
    else:
        user_form = forms.UserRegistrationForm()
        profile_form = forms.IndividualProfileRegistrationForm()
        context = {"user_form": user_form,
                   "profile_form": profile_form}
        return shortcuts.render(request, template_name="users/individual_registration.html", context=context)


def organization_registration_view(request):

    if request.method == "POST":
        user_form = forms.UserRegistrationForm(request.POST)
        profile_form = forms.OrganizationProfileRegistrationForm(request.POST)
        org_form = forms.OrganizationRegistrationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid() \
                and org_form.is_valid():

            # Save organization linked to the user
            org = org_form.save(commit=False)
            org.save()

            # Save user as org_admin with premium
            user = user_form.save(commit=False)
            user.role = 'org_admin'
            user.is_premium = True  # Org admins get premium
            user.save()

            profile = profile_form.save(commit=False)
            profile.organization = org
            profile.user = user
            profile.save()
            # Email verification and messages
            messages.success(
                request, 'Organization registered! Verify your email.')
            email_manager.mail_verification(request, user)
            return shortcuts.redirect('users:login')

        # Handle form errors
        messages.error(request, 'Invalid form submission.')
        return shortcuts.redirect('users:register')

    else:

        user_form = forms.UserRegistrationForm()
        profile_form = forms.OrganizationProfileRegistrationForm()
        org_form = forms.OrganizationRegistrationForm()
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "org_form": org_form
        }
        return shortcuts.render(request, 'users/organization_registration.html',
                                context=context)


def login_non_verified_email(request, email):
    """
    Redirects the user to the login page and displays a message depending on
    the user's email verification status.

    If the user's email is not verified and a verification email has been sent
    within the last 10 minutes, the user is asked to wait. If the user's email
    is not verified and a verification email has not been sent within the last
    10 minutes, the user is given the option to resend the verification email.

    If the user's email is verified, the user is given an error message and
    redirected to the login page.

    If the user's email is not found, the user is given an error message and
    redirected to the login page.
    """
    print("Login request. Email: %s", email)

    try:
        user = User.objects.get(email=email)
        print("User found: %s", user)
    except User.DoesNotExist:
        print("User not found")
        messages.error(request, UserMessageManager.email_not_found)
        return shortcuts.redirect("users:login")

    if user.email_verified:
        print("Email already verified")
        messages.error(request, UserMessageManager.email_not_verified)
        return shortcuts.redirect("users:login")

    timeout_duration = datetime.timedelta(minutes=10)

    if user.last_verification_email_sent:
        print("Email already sent")
        time_since_last_email = utils.get_time_since_last_email(
            user.last_verification_email_sent
        )

        can_resend = utils.get_can_resend(
            timeout_duration, time_since_last_email)

        if can_resend:
            url = urls.reverse("users:resend")
            message = UserMessageManager.resend_verification_email(url)
        else:
            minutes_difference = utils.get_minutes_left_before_resend(
                time_since_last_email, timeout_duration
            )
            minutes_difference = round(minutes_difference)
            message = UserMessageManager.resend_email_wait(
                minutes_difference)
    else:
        print("Email not sent")
        url = urls.reverse("users:resend")
        message = UserMessageManager.resend_verification_email(url)

    messages.info(request, message)
    return shortcuts.redirect("users:login")


def login_view(request):
    print(f"Login request. Method: {request.method}")

    # Handle POST request
    if request.method == "POST":
        form = forms.LoginForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Check if the honeypot field is filled
            if form.cleaned_data["honeypot"]:
                messages.error(request, UserMessageManager.spam)
                return shortcuts.redirect("core:home")

            # Retrieve the email and password
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = auth.authenticate(request, email=email, password=password)

            # Sign in the user if the email has been verified
            if user is not None:
                if user.email_verified:
                    for backend in auth.get_backends():
                        if user == backend.get_user(user.id):
                            user.backend = (
                                f"{backend.__module__}.{backend.__class__.__name__}"
                            )
                            break

                    auth.login(request, user)
                    print(f"ROLE: {user.role}")
                    if user.role == "individual":
                        return shortcuts.redirect("individual:dashboard")
                    elif user.role == "org_admin":
                        return shortcuts.redirect("organization:dashboard")
                    else:
                        return shortcuts.redirect("users:login")

            else:
                print("Email not verified")
                # Handle non-verified email login attempts
                return login_non_verified_email(request, email)
        else:
            messages.error(request, UserMessageManager.invalid_login_form)
            return shortcuts.redirect("users:login")
    else:
        form = forms.LoginForm()

    context = {"form": form}
    return shortcuts.render(request, "users/login.html", context)


def verify_email_view(request, user_id, token):
    """
    View that verifies a user's email address.

    Args:
        - request (`django.http.HttpRequest`): The request object.
        - user_id (`int`): The ID of the user to verify.
        - token (`str`): The verification token.

    Returns:
        - A redirect to the login page if the token is valid,
        or a 404 if the user or token is invalid.

    """
    from users.tokens import email_verification_token  # Import the token generator

    user = shortcuts.get_object_or_404(User, id=user_id)

    if email_verification_token.check_token(user, token):
        user.email_verified = True
        user.save()
        messages.success(request, UserMessageManager.email_verified)
        return shortcuts.redirect("users:login")


def resend_view(request):
    """
    A view that handles the resend verification email form submission.

    If the form is valid, it sends a verification email to the user and
    redirects to the login page. If the form is invalid, it redirects to
    the home page with an error message.

    Args:
        - request (`django.http.HttpRequest`): The request object.

    Returns:
        - `django.http.HttpResponse`: The response object.
    """
    if request.method == "POST":
        form = forms.ResendVerificationEmailForm(request.POST)

        if form.is_valid():
            if form.cleaned_data["honeypot"]:
                messages.error(request, UserMessageManager.spam)

                return shortcuts.redirect("core:home")
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, UserMessageManager.email_not_found)
                return shortcuts.redirect("users:resend")

            timeout_duration = datetime.timedelta(minutes=10)

            if user.last_verification_email_sent:
                # Calculate the time difference between the current time and
                # the last time the verification email was sent
                time_since_last_email = utils.get_time_since_last_email(
                    user.last_verification_email_sent
                )

                # Calculate the time difference between the timeout duration
                # and the time since the last verification email was sent
                minutes_difference = utils.get_minutes_left_before_resend(
                    time_since_last_email, timeout_duration
                )

                # If the time difference is less than the timeout duration,
                # show an info message to the user to wait
                if time_since_last_email < timeout_duration:
                    messages.info(
                        request,
                        UserMessageManager.resend_email_wait(
                            minutes_difference),
                    )
                    return shortcuts.redirect("users:resend")

            # Send the verification email and save the last verification email
            # sent time
            email_manager.mail_verification(request, user)
            user.last_verification_email_sent = timezone.now()
            user.save()

            messages.success(
                request, UserMessageManager.email_verification_sent)
            return shortcuts.redirect("users:login")
    else:
        form = forms.ResendVerificationEmailForm()

    return shortcuts.render(request, "users/resend.html", {"form": form})


@login_required
def logout_view(request):
    """
    Log out the user and redirect to the home page.

    This view logs out the currently authenticated user and
    redirects them to the home page. It requires the user to
    be logged in before accessing it.

    Args:
        request: The HTTP request object.

    Returns:
        A redirect to the home page.
    """

    auth.logout(request)
    return shortcuts.redirect("users:login")


def password_reset_view(request):
    """
    A view that handles the password reset form submission.

    This view verifies the form and sends an email to the user with a
    password reset link. If the form is invalid, it redirects to the
    home page with an error message.

    Args:
        - request (`django.http.HttpRequest`): The request object.

    Returns:
        - `django.http.HttpResponse`: The response object.
    """
    if request.method == "POST":
        form = forms.PasswordResetForm(request.POST)
        if form.is_valid():
            # Check if the honeypot field is filled
            if form.cleaned_data["honeypot"]:
                messages.error(request, UserMessageManager.spam)
                return shortcuts.redirect("home:home")

            # Retrieve the email from the form
            email = form.cleaned_data["email"]

            # Check if the user exists
            user = User.objects.filter(email=email).first()
            if user:
                # Send the password reset email
                email_manager.mail_password_reset(request, user)
                messages.success(
                    request, UserMessageManager.password_reset_success)
                return shortcuts.redirect("users:password_reset")
            else:
                # If the user does not exist, show an error message
                messages.error(request, UserMessageManager.email_not_found)
            return shortcuts.redirect("users:password_reset")
    else:
        # If the request is GET,
        # create an empty form
        form = forms.PasswordResetForm()
    return shortcuts.render(request, "users/password_reset.html", {"form": form})


@login_required
def delete_account_view(request):
    """Delete a user account

    This view is used to delete a user account. If the request
    method is POST, it deletes the user and their associated
    profile.

    If the request method is GET, it renders a confirmation page
    asking the user whether they want to delete their account.

    Args:
        - request: The HTTP request object

    Returns:
        - A redirect to the home page if the request method is POST
        - A confirmation page if the request method is GET
    """

    if request.method == "POST":
        user = request.user
        user.profile.delete()
        user.delete()
        messages.success(
            request, UserMessageManager.account_deleted_success)
        return shortcuts.redirect("home:home")

    # Render the confirmation page
    return shortcuts.render(request, "users/delete_account.html")
