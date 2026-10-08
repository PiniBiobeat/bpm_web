from logic.pages.forgot_password_page import ForgotPasswordPage
from logic.pages.login_page import LogInOnline


def test_login_with_expired_password_opens_reset_password_screen(
    login_page: LogInOnline, forgot_password_page: ForgotPasswordPage, expired_user
):
    login_page.login(expired_user.email, expired_user.password)

    forgot_password_page.expect_password_expired_message_visible()
    forgot_password_page.expect_verification_screen_opened()
    forgot_password_page.expect_resend_button_visible()
    forgot_password_page.expect_back_to_login_visible()
