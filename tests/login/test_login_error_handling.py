import pytest

from logic.pages.login_page import LogInOnline

VALID_EMAIL = "pini.mari@bio-beat.com"

EMAIL_REQUIRED_ERROR = "email is required"
PASSWORD_REQUIRED_ERROR = "Password is required"
INCORRECT_CREDENTIALS_ERROR = "Incorrect email or password"


def test_login_with_invalid_credentials_shows_error(login_page: LogInOnline):
    login_page.login("wrong.user@bio-beat.com", "Pm123456!")

    login_page.expect_login_rejected()


def test_login_with_empty_email_and_password(login_page: LogInOnline):
    login_page.login("", "")

    login_page.expect_error_message(EMAIL_REQUIRED_ERROR)
    login_page.expect_email_marked_invalid()


def test_login_with_empty_password(login_page: LogInOnline):
    login_page.login(VALID_EMAIL, "")

    login_page.expect_error_message(PASSWORD_REQUIRED_ERROR)
    login_page.expect_password_marked_invalid()


def test_login_with_empty_email(login_page: LogInOnline):
    login_page.login("", "123456")

    login_page.expect_error_message(EMAIL_REQUIRED_ERROR)
    login_page.expect_email_marked_invalid()


@pytest.mark.parametrize(
    ("email", "password"),
    [
        pytest.param("user@,user.com", "123456", id="invalid_email_format"),
        pytest.param("wrong@bio-beat.com", "ValidPassword123", id="wrong_email"),
        pytest.param("deleted.user@bio-beat.com", "ValidPassword123", id="deleted_user"),
        pytest.param(VALID_EMAIL, "12", id="short_password"),
    ],
)
def test_login_with_rejected_credentials_shows_incorrect_credentials_error(
    login_page: LogInOnline, email: str, password: str
):
    login_page.login(email, password)

    login_page.expect_error_message(INCORRECT_CREDENTIALS_ERROR)
