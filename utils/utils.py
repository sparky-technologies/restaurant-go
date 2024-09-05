import random
import traceback
import uuid
from utils.mails import sendmail
import logging
from typing import Union
import string

logger = logging.getLogger(__name__)


def send_otp(email: Union[str, None], username: Union[str, None]) -> Union[str, None]:
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
        otp = "".join(filter(str.isdigit, uuid_hex))[:4]

        message = f"""
        Your One Time Password is {otp}
        <br />
        Expires in 10 minutes
        """
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


def send_reset_otp(email: Union[str, None]) -> Union[str, None]:
    """
    This function generates an One Time Password (OTP) and sends it to the specified email address.

    Args:
        email (str): The email address of the user.

    Returns:
        str: The OTP that was sent to the email address.

    Raises:
        ValueError: If the email is not provided, a ValueError is raised.
    """
    try:
        if not email:
            raise ValueError("Email must be provided")

        uid = uuid.uuid4()
        uuid_hex = uid.hex  # convert to hex value
        otp = "".join(filter(str.isdigit, uuid_hex))[:4]

        message = f"""
        Your One Time Reset Password is {otp}
        <br />
        Expires in 10 minutes
        """
        sendmail(
            subject="Password Reset Code",
            message=message,
            user_email=email,
        )

        return otp
    except ValueError:
        raise ValueError("Email must be provided")
    except Exception as e:
        logger.error(f"Error sending email to {email} due to {e}")
        traceback.print_exc()
        return None


def generate_ref() -> str:
    """generate unique reference code"""
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return code.upper()
