import pytest
from unittest.mock import patch, MagicMock
from utils.utils import send_otp, send_reset_otp


@pytest.mark.parametrize(
    "email, username",
    [
        ("", "test_user"),  # Empty email
        ("test@example.com", ""),  # Empty username
    ],
)
def test_send_otp_missing_input(email, username):
    with pytest.raises(ValueError):
        send_otp(email, username)


@pytest.mark.parametrize(
    "email, username",
    [
        ("test@example.com", "test_user"),
        ("another@example.com", "another_user"),
    ],
)
def test_send_otp_valid_input(email, username):
    with patch("utils.utils.sendmail") as mocked_sendmail:
        otp = send_otp(email, username)

        assert otp is not None
        assert len(otp) == 4
        message = f"""
        Your One Time Password is {otp}
        <br />
        Expires in 10 minutes
        """
        mocked_sendmail.assert_called_once_with(
            subject="Email Verification Code",
            message=message,
            user_email=email,
            username=username,
        )


@pytest.mark.parametrize(
    "email, username",
    [
        ("test@example.com", "test_user"),
        ("another@example.com", "another_user"),
    ],
)
def test_send_otp_exception(email, username):
    with patch("utils.utils.sendmail") as mocked_sendmail:
        mocked_sendmail.side_effect = Exception("Email sending failed")

        otp = send_otp(email, username)

        assert otp is None


# Test to handle exceptions raised by the sendmail function
@pytest.mark.parametrize("email", ["test@example.com"])
def test_send_reset_otp_sendmail_exception(email):
    with patch("utils.utils.sendmail") as mocked_sendmail:
        mocked_sendmail.side_effect = Exception("Email sending failed")
        with patch("utils.utils.logger") as mocked_logger:
            otp = send_reset_otp(email)
            assert otp is None
            mocked_logger.error.assert_called_once_with(
                f"Error sending email to {email} due to Email sending failed"
            )


# Test to verify logging when an exception occurs
@pytest.mark.parametrize("email", ["test@example.com"])
def test_send_reset_otp_logging_exception(email):
    with patch("utils.utils.sendmail") as mocked_sendmail:
        mocked_sendmail.side_effect = Exception("Email sending failed")
        with patch("utils.utils.logger") as mocked_logger:
            otp = send_reset_otp(email)
            assert otp is None
            mocked_logger.error.assert_called_once()


# Test to verify the return value when sendmail fails
@pytest.mark.parametrize("email", ["test@example.com"])
def test_send_reset_otp_sendmail_failure(email):
    with patch("utils.utils.sendmail") as mocked_sendmail:
        mocked_sendmail.side_effect = Exception("Email sending failed")
        otp = send_reset_otp(email)
        assert otp is None


# Existing valid test case
@pytest.mark.parametrize("email", ["test@example.com"])
def test_send_reset_otp(email):
    with patch("utils.utils.sendmail") as mocked_sendmail:
        otp = send_reset_otp(email)
        assert otp is not None
        assert len(otp) == 6
        message = f"""
        Your One Time Reset Password is {otp}
        <br />
        Expires in 10 minutes
        """
        mocked_sendmail.assert_called_once_with(
            subject="Password Reset Code",
            message=message,
            user_email=email,
        )
