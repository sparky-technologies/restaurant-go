import pytest
from unittest.mock import patch, MagicMock
from utils.mails import sendmail


@pytest.mark.parametrize(
    "user_email, other_email",
    [
        ("test@example.com", None),  # Single recipient
        ("test@example.com", "other@example.com"),  # Multiple recipients
    ],
)
def test_sendmail_success(user_email, other_email):
    with patch("utils.mails.sendmail") as MockEmailMessage:

        # Call the function
        subject = "Test Subject"
        message = "Test Message"
        username = "Test User"
        sendmail(subject, message, user_email, username, other_email=other_email)

        # Assert that EmailMessage is instantiated correctly
        if other_email:
            MockEmailMessage.assert_called_once_with(
                subject, message, "truebone002@gmail.com", [user_email, other_email]
            )
        else:
            MockEmailMessage.assert_called_once_with(
                subject, message, "truebone002@gmail.com", [user_email]
            )
