import traceback
import uuid
from utils.mails import sendmail
import logging
from typing import Union

logger = logging.getLogger(__name__)


def send_otp(email: str, username: str) -> Union[str, None]:
    """
    This function generates an One Time Password (OTP) and sends it to the specified email address.

    Args:
        email (str): The email address of the user.
        username (str): The username of the user.

    Returns:
        str: The OTP that was sent to the email address.

    Raises:
        ValueError: If the email or username is not provided, a ValueError is raised.
    """
    try:
        if not email or not username:
            raise ValueError("Email and username must be provided")

        uid = uuid.uuid4()
        uuid_hex = uid.hex  # convert to hex value
        otp = "".join(filter(str.isdigit, uuid_hex))[:6]

        message = f"Your One Time Password is {otp}"
        sendmail(
            subject="Email Verification Code",
            message=message,
            user_email=email,
            username=username,
        )

        return otp
    except ValueError:
        raise ValueError("Email and username must be provided")
    except Exception as e:
        logger.error(f"Error sending email to {email} due to {e}")
        traceback.print_exc()
        return None
