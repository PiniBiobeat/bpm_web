from logic.pages.login_page import LogInOnline

RESET_EMAIL = "pini.mari@bio-beat.com"


def test_open_forgot_password_page(login_page: LogInOnline):
    forgot_password_page = login_page.open_forgot_password()

    forgot_password_page.expect_forgot_password_page_opened()


def test_request_code_opens_verification_screen(login_page: LogInOnline):
    forgot_password_page = login_page.open_forgot_password()

    forgot_password_page.request_code(RESET_EMAIL)

    forgot_password_page.expect_verification_screen_opened()
