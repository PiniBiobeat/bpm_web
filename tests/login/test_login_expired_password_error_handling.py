import pytest

from logic.pages.forgot_password_page import ForgotPasswordPage

VALID_CODE = "123456"
WRONG_CODE = "000000"
VALID_PASSWORD = "Valid@123"
MISMATCHED_PASSWORD = "Invalid@123"
WEAK_PASSWORD = "abc"

PASSWORD_PREVIOUSLY_USED_ERROR = "Password has previously been used"
PASSWORD_COMPLEXITY_ERROR = (
    "Password must have at least 8 characters, and contain upper case, lower case, numeric, and special characters"
)
PASSWORDS_DO_NOT_MATCH_ERROR = "Passwords do not match"
CODE_REQUIRED_ERROR = "Verification code is required"
CODE_EMPTY_ERROR = "Verification code cannot be empty"
PASSWORD_EMPTY_ERROR = "Password cannot be empty"
CONFIRM_PASSWORD_REQUIRED_ERROR = "Please confirm password to continue"
INVALID_CODE_ERROR = "Invalid verification code provided, please try again"


def test_expired_password_change_with_last_used_password_shows_error(
    expired_password_page: ForgotPasswordPage, expired_user_with_code
):
    expired_password_page.change_password(
        expired_user_with_code.verification_code,
        expired_user_with_code.used_password,
        expired_user_with_code.used_password,
    )

    expired_password_page.expect_reset_password_error_message(PASSWORD_PREVIOUSLY_USED_ERROR)


def test_expired_password_change_with_invalid_password_shows_error(
    expired_password_page: ForgotPasswordPage, expired_user_with_code
):
    expired_password_page.change_password(
        expired_user_with_code.verification_code, WEAK_PASSWORD, WEAK_PASSWORD
    )

    expired_password_page.expect_reset_password_error_message(PASSWORD_COMPLEXITY_ERROR)


@pytest.mark.parametrize(
    ("code", "password", "confirm_password", "expected_error"),
    [
        pytest.param(VALID_CODE, VALID_PASSWORD, MISMATCHED_PASSWORD, PASSWORDS_DO_NOT_MATCH_ERROR, id="confirm_mismatch"),
        pytest.param("", VALID_PASSWORD, VALID_PASSWORD, CODE_EMPTY_ERROR, id="empty_code"),
        pytest.param(VALID_CODE, "", "", PASSWORD_EMPTY_ERROR, id="empty_password"),
        pytest.param(VALID_CODE, VALID_PASSWORD, "", CONFIRM_PASSWORD_REQUIRED_ERROR, id="empty_confirm"),
        pytest.param(WRONG_CODE, VALID_PASSWORD, VALID_PASSWORD, INVALID_CODE_ERROR, id="wrong_code"),
    ],
)
def test_expired_password_change_with_invalid_input_shows_error(
    expired_password_page: ForgotPasswordPage,
    code: str,
    password: str,
    confirm_password: str,
    expected_error: str,
):
    expired_password_page.change_password(code, password, confirm_password)

    expired_password_page.expect_reset_password_error_message(expected_error)


def test_expired_password_change_with_all_fields_empty_shows_verification_code_required(
    expired_password_page: ForgotPasswordPage,
):
    expired_password_page.click_change_password()

    expired_password_page.expect_reset_password_error_message(CODE_REQUIRED_ERROR)
