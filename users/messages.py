

class BaseMessageManager:
    spam = "Your form submission was detected as spam."


class UserMessageManager(BaseMessageManager):
    invalid_password = "Please enter a valid password."
    invalid_email = "Please enter a valid email address."

    profile_update_success = "Your profile has been updated!"
    email_not_found = "We can't find a user with that email address."
    account_deleted_success = "Your account has been successfully deleted."
    email_verification_sent = "A verification email has been sent."

    email_not_verified = "Your email has not been verified yet."
    email_verified = "Your email has been verified. You can now log in."
    email_already_verified = "Your email has already been verified."

    password_reset_success = """We've emailed you instructions for setting your password, 
        if an account exists with the email you entered. You should receive them 
        shortly. If you don't receive an email, please make sure you've entered the 
        address you registered with, and check your spam folder."""

    invalid_login_form = "Login form is not valid"

    invalid_birth_date = "Please enter a valid date of birth."

    @staticmethod
    def resend_email_wait(minutes):
        return f"Please wait {minutes} before resending the verification email."

    @staticmethod
    def resend_verification_email(url):
        return f""" 

            Please verify your email before logging in. 

            Please check your email for the verification link, including spam folder. 

            If you need to resend the verification email, please click <a href='{url}'>here</a>. 

            """
