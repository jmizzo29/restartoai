from django.utils import timezone


def get_time_since_last_email(last_email_sent):
    """
    Calculates the time elapsed since the last verification email was sent.

    Args:
        - last_email_sent (`datetime`): The timestamp when the last email was sent.

    Returns:
        - `timedelta`: The time difference between the current time and the
        last email sent time.
    """
    return timezone.now() - last_email_sent


def get_can_resend(timeout_duration, time_since_last_email):
    """
    Checks if the time since the last verification email was sent is greater than
    the timeout duration.

    Args:
        - timeout_duration (`timedelta`): The duration of time after which
        the user can resend the verification email.
        - time_since_last_email (`timedelta`): The time elapsed since the last
        verification email was sent.

    Returns:
        - `bool`: True if the user can resend the verification email, False
        otherwise.
    """
    return time_since_last_email > timeout_duration


def get_minutes_left_before_resend(time_since_last_email, timeout_duration):
    """
    Calculates the remaining minutes before a user can resend the verification email.

    Args:
        - time_since_last_email (`timedelta`): The time elapsed since the last
        verification email was sent.
        - timeout_duration (`timedelta`): The duration after which the user
        can resend the verification email.

    Returns:
        - `float`: The number of minutes left before the user can resend the
        verification email.
    """

    time_difference = timeout_duration - time_since_last_email
    total_seconds = time_difference.total_seconds()
    return total_seconds // 60
