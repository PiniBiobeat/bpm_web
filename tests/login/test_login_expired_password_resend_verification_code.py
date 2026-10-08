from logic.pages.forgot_password_page import ForgotPasswordPage


def test_expired_password_resend_button_visible(expired_password_page: ForgotPasswordPage):
    expired_password_page.expect_resend_button_visible()
