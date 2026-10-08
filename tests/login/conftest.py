import os
from dataclasses import dataclass

import pytest

from logic.pages.forgot_password_page import ForgotPasswordPage
from logic.pages.login_page import LogInOnline
from logic.pages.session_management_page import SessionManagementPage


@dataclass(frozen=True)
class UserCredentials:
    email: str
    password: str


@dataclass(frozen=True)
class ExpiredUser(UserCredentials):
    verification_code: str = ""
    used_password: str = ""


@pytest.fixture
def metric_user() -> UserCredentials:
    email = os.getenv("ADMIN_METRIC_EMAIL")
    password = os.getenv("ADMIN_METRIC_PASSWORD")
    if not email or not password:
        pytest.skip("Set ADMIN_METRIC_EMAIL and ADMIN_METRIC_PASSWORD to run this test.")
    return UserCredentials(email, password)


@pytest.fixture
def expired_user() -> ExpiredUser:
    email = os.getenv("EXPIRED_USER_EMAIL")
    password = os.getenv("EXPIRED_USER_PASSWORD")
    if not email or not password:
        pytest.skip("Set EXPIRED_USER_EMAIL and EXPIRED_USER_PASSWORD to run this test.")
    return ExpiredUser(
        email=email,
        password=password,
        verification_code=os.getenv("EXPIRED_USER_VERIFICATION_CODE", ""),
        used_password=os.getenv("EXPIRED_USER_USED_PASSWORD", password),
    )


@pytest.fixture
def session_page(login_page: LogInOnline) -> SessionManagementPage:
    return SessionManagementPage(login_page.pw_page)


@pytest.fixture
def expired_user_with_code(expired_user: ExpiredUser) -> ExpiredUser:
    if not expired_user.verification_code:
        pytest.skip("Set EXPIRED_USER_VERIFICATION_CODE for this test.")
    return expired_user


@pytest.fixture
def forgot_password_page(login_page: LogInOnline) -> ForgotPasswordPage:
    """Page object for the reset-password screens; does not navigate by itself."""
    return ForgotPasswordPage(login_page.pw_page)


@pytest.fixture
def expired_password_page(
    login_page: LogInOnline, forgot_password_page: ForgotPasswordPage, expired_user: ExpiredUser
) -> ForgotPasswordPage:
    """Logs in as the expired user and returns the reset-password screen it lands on."""
    login_page.login(expired_user.email, expired_user.password)
    if not forgot_password_page.verify_verification_screen_opened():
        pytest.skip("Expired-password reset screen did not open for configured credentials.")
    return forgot_password_page
