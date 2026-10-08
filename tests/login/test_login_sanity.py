import pytest

from logic.pages.login_page import LogInOnline
from logic.pages.session_management_page import SessionManagementPage

SESSION_MANAGEMENT_URL = "https://bpholter.stage.bio-beat.cloud/session-management"
EXPECTED_CLIENT_NAME = "pinitesting"


@pytest.mark.smoke
def test_open_login_page(login_page: LogInOnline):
    login_page.expect_login_page_opened()


@pytest.mark.smoke
def test_login_with_valid_credentials_sanity(
    login_page: LogInOnline, session_page: SessionManagementPage, metric_user
):
    login_page.login(metric_user.email, metric_user.password)

    session_page.expect_url(SESSION_MANAGEMENT_URL)
    session_page.expect_session_management_page_opened()
    session_page.expect_session_grid_opened()
    session_page.expect_header_and_navigation_visible()


@pytest.mark.smoke
def test_login_and_check_settings_menu_opens_sanity(
    login_page: LogInOnline, session_page: SessionManagementPage, metric_user
):
    login_page.login(metric_user.email, metric_user.password)
    session_page.expect_session_management_page_opened()

    session_page.open_settings_menu()
    session_page.expect_settings_menu_opened()
    session_page.expect_email_support_visible()
    session_page.expect_choose_department_visible()
    session_page.expect_settings_client_name(EXPECTED_CLIENT_NAME)
    session_page.expect_settings_user_email_visible(metric_user.email)

    session_page.click_logout()
    login_page.expect_login_page_opened()
