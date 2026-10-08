import pytest

from logic.pages.login_page import LogInOnline

EMAIL_REQUIRED_ERROR = "Email is required"
INVALID_EMAIL_ERROR = "Please enter a valid email address"


@pytest.mark.parametrize(
    ("email", "expected_error"),
    [
        pytest.param("", EMAIL_REQUIRED_ERROR, id="empty_email"),
        pytest.param("user", INVALID_EMAIL_ERROR, id="malformed_email"),
    ],
)
def test_reset_password_request_code_with_invalid_email_shows_error(
    login_page: LogInOnline, email: str, expected_error: str
):
    forgot_password_page = login_page.open_forgot_password()

    forgot_password_page.request_code(email)

    forgot_password_page.expect_email_error_message(expected_error)
    forgot_password_page.expect_email_marked_invalid()
