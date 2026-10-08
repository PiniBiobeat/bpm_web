from infra.page_base import PageBase
import re
from playwright.sync_api import expect


class ForgotPasswordPage(PageBase):
    EMAIL_INPUT = "input[type='email'], input[name='email'], input[placeholder='Email *']"
    BACK_TO_LOGIN = "button:has-text('Back to Login'), button:has-text('Back to login page')"
    REQUEST_CODE = "//button[text()='Request Code']"
    VERIFICATION_CODE_INPUT = (
        "input[name*='Verification Code *'], input[placeholder*='Verification'], input[placeholder*='code']"
    )
    NEW_PASSWORD_INPUT = "input[placeholder='New Password']"
    CONFIRM_PASSWORD_INPUT = "input[placeholder='Confirm New Password']"
    CHANGE_PASSWORD_BUTTON = (
        "button:has-text('Reset Password'), button:has-text('Change Password'), button:has-text('Change password')"
    )
    RESEND_BUTTON = "button:has-text('Resend')"
    PASSWORD_EXPIRED_MESSAGE = "Your password has expired"
    EMAIL_ERROR = "text=/email is required|please enter a valid email address|invalid email/i"

    def verify_forgot_password_page_opened(self):
        try:
            self.pw_page.locator(self.EMAIL_INPUT).first.wait_for(state="visible", timeout=10000)
            self.pw_page.locator(self.BACK_TO_LOGIN).first.wait_for(state="visible", timeout=10000)
            self.pw_page.locator(self.REQUEST_CODE).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    def enter_email(self, email: str):
        self.pw_page.locator(self.EMAIL_INPUT).first.fill(email)

    def click_request_code(self):
        self.pw_page.locator(self.REQUEST_CODE).first.click()

    def click_back_to_login(self):
        self.pw_page.locator(self.BACK_TO_LOGIN).first.click()

    def request_code(self, email: str):
        self.enter_email(email)
        self.click_request_code()

    def enter_verification_code(self, code: str):
        self.pw_page.locator(self.VERIFICATION_CODE_INPUT).first.fill(code)

    def enter_new_password(self, password: str):
        self.pw_page.locator(self.NEW_PASSWORD_INPUT).first.fill(password)

    def enter_confirm_password(self, password: str):
        self.pw_page.locator(self.CONFIRM_PASSWORD_INPUT).first.fill(password)

    def click_change_password(self):
        self.pw_page.locator(self.CHANGE_PASSWORD_BUTTON).first.click()

    def change_password(self, verification_code: str, new_password: str, confirm_password: str):
        self.enter_verification_code(verification_code)
        self.enter_new_password(new_password)
        self.enter_confirm_password(confirm_password)
        self.click_change_password()

    def verify_verification_screen_opened(self):
        try:
            self.pw_page.locator(self.VERIFICATION_CODE_INPUT).first.wait_for(state="visible", timeout=15000)
            self.pw_page.locator(self.NEW_PASSWORD_INPUT).first.wait_for(state="visible", timeout=15000)
            self.pw_page.locator(self.CONFIRM_PASSWORD_INPUT).first.wait_for(state="visible", timeout=15000)
            self.pw_page.locator(self.CHANGE_PASSWORD_BUTTON).first.wait_for(state="visible", timeout=15000)
            return True
        except Exception:
            return False

    def verify_email_error_message(self, expected_message: str):
        expected_message = self._normalize_text(expected_message)
        if not expected_message:
            return False

        email_input = self.pw_page.locator(self.EMAIL_INPUT).first

        try:
            exact_error = self.pw_page.get_by_text(expected_message, exact=False).first
            if exact_error.is_visible(timeout=2000):
                exact_text = self._normalize_text(exact_error.text_content() or "")
                if exact_text == expected_message:
                    return True
        except Exception:
            pass

        try:
            ui_error = self.pw_page.locator(self.EMAIL_ERROR).first
            if ui_error.is_visible(timeout=2000):
                ui_text = self._normalize_text(ui_error.text_content() or "")
                if expected_message == ui_text:
                    return True
        except Exception:
            pass

        try:
            validation_message = self._normalize_text(email_input.evaluate("el => el.validationMessage") or "")
            if expected_message == validation_message:
                return True
        except Exception:
            pass

        return False

    def verify_email_marked_red(self):
        email_input = self.pw_page.locator(self.EMAIL_INPUT).first

        try:
            if email_input.get_attribute("aria-invalid") == "true":
                return True
        except Exception:
            pass

        try:
            class_name = (email_input.get_attribute("class") or "").lower()
            if "error" in class_name or "invalid" in class_name:
                return True
        except Exception:
            pass

        try:
            border_color = (email_input.evaluate("el => getComputedStyle(el).borderColor") or "").lower()
            return "255, 0, 0" in border_color or "220, 38, 38" in border_color or "red" in border_color
        except Exception:
            return False

    def verify_reset_password_error_message(self, expected_message: str):
        expected_message = self._normalize_text(expected_message)
        if not expected_message:
            return False

        try:
            matched = self.pw_page.get_by_text(expected_message, exact=False).first
            if matched.is_visible(timeout=4000):
                actual = self._normalize_text(matched.text_content() or "")
                if actual == expected_message or expected_message in actual:
                    return True
        except Exception:
            pass

        for selector in ["[class*='error']", "[role='alert']", "[aria-live='assertive']"]:
            try:
                locator = self.pw_page.locator(selector)
                for idx in range(locator.count()):
                    item = locator.nth(idx)
                    if not item.is_visible(timeout=1000):
                        continue
                    actual = self._normalize_text(item.text_content() or "")
                    if actual == expected_message or expected_message in actual:
                        return True
            except Exception:
                continue

        for field_selector in [self.VERIFICATION_CODE_INPUT, self.NEW_PASSWORD_INPUT, self.CONFIRM_PASSWORD_INPUT]:
            try:
                message = self._normalize_text(
                    self.pw_page.locator(field_selector).first.evaluate("el => el.validationMessage") or ""
                )
                if message == expected_message or expected_message in message:
                    return True
            except Exception:
                continue

        return False

    def _normalize_text(self, value: str):
        text = (value or "").strip().lower()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return " ".join(text.split())

    # ---- Assertions -------------------------------------------------------

    def expect_forgot_password_page_opened(self):
        expect(self.pw_page.locator(self.EMAIL_INPUT).first).to_be_visible(timeout=10000)
        expect(self.pw_page.locator(self.BACK_TO_LOGIN).first).to_be_visible(timeout=10000)
        expect(self.pw_page.locator(self.REQUEST_CODE).first).to_be_visible(timeout=10000)

    def expect_verification_screen_opened(self):
        expect(self.pw_page.locator(self.VERIFICATION_CODE_INPUT).first).to_be_visible(timeout=15000)
        expect(self.pw_page.locator(self.NEW_PASSWORD_INPUT).first).to_be_visible(timeout=15000)
        expect(self.pw_page.locator(self.CONFIRM_PASSWORD_INPUT).first).to_be_visible(timeout=15000)
        expect(self.pw_page.locator(self.CHANGE_PASSWORD_BUTTON).first).to_be_visible(timeout=15000)

    def expect_password_expired_message_visible(self):
        expect(self.pw_page.get_by_text(self.PASSWORD_EXPIRED_MESSAGE).first).to_be_visible(timeout=15000)

    def expect_resend_button_visible(self):
        expect(self.pw_page.locator(self.RESEND_BUTTON).first).to_be_visible(timeout=10000)

    def expect_back_to_login_visible(self):
        expect(self.pw_page.locator(self.BACK_TO_LOGIN).first).to_be_visible(timeout=10000)

    def expect_email_error_message(self, expected_message: str):
        assert self.verify_email_error_message(expected_message), (
            f"Expected email error '{expected_message}' to be displayed."
        )

    def expect_email_marked_invalid(self):
        assert self.verify_email_marked_red(), "Expected the email field to be marked as invalid."

    def expect_reset_password_error_message(self, expected_message: str):
        assert self.verify_reset_password_error_message(expected_message), (
            f"Expected reset-password error '{expected_message}' to be displayed."
        )
