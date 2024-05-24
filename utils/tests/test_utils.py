import pytest
from unittest.mock import patch, MagicMock
from utils.utils import send_otp


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
        assert len(otp) == 6
        mocked_sendmail.assert_called_once_with(
            subject="Email Verification Code",
            message=f"Your One Time Password is {otp}",
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
