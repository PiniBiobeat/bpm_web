import os
import pytest

from infra.config.config_provider import configuration
from logic.pages.login_page import LogInOnline
from logic.pages.patient_admission_page import PatientAdmissionPage
from logic.pages.session_management_page import SessionManagementPage
from tests.test_base_online import TestBaseOnline


SESSION_URL_FRAGMENT = "session-management"
ADMIN_EMAIL = os.getenv("ADMIN_METRIC_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_METRIC_PASSWORD")
USED_DEVICE_ID = os.getenv("USED_DEVICE_ID")
USED_DEVICE_ID_ERROR = os.getenv("USED_DEVICE_ID_ERROR", "Device ID already exists")
INACTIVE_DEVICE_ID = os.getenv("INACTIVE_DEVICE_ID", "111111211")
INACTIVE_DEVICE_ID_ERROR = os.getenv(
    "INACTIVE_DEVICE_ID_ERROR", "Device is not activated or does not exist."
)


class TestAdministratorRoleMetricForm(TestBaseOnline):

    def _login_and_open_patient_admission(self):
        page: LogInOnline = self.browser_online.navigate(configuration["online_url"], LogInOnline)
        assert page.verify_login_page_opened(), "Login page did not load for administrator scenario."

        page.login(ADMIN_EMAIL, ADMIN_PASSWORD)

        session_page = SessionManagementPage(page.pw_page)
        assert session_page.verify_session_management_page_opened(), (
            "Session management page did not load after administrator login."
        )
        assert session_page.verify_session_grid_opened(), (
            "Session grid controls or columns are not visible on session management page."
        )

        patient_admission_page: PatientAdmissionPage = session_page.open_patient_admission()
        assert patient_admission_page.verify_opened(), (
            "Patient admission form did not open with required fields and confirm action. "
            f"Details: {patient_admission_page.get_last_open_failure()}"
        )
        return page, session_page, patient_admission_page

    @pytest.mark.usefixtures("before_after_test")
    def test_all_fields_empty_show_errors(self):
        _, _, page = self._login_and_open_patient_admission()
        page.click_confirm()
        assert page.verify_error_message("Patient ID is required")
        assert page.verify_error_message("Device ID is required")
        assert page.verify_error_message("Gender is required")
        assert page.verify_error_message("Weight is required")
        assert page.verify_error_message("Height is required")
        assert page.verify_error_message("Please enter physician name")

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_patient_id_max_length_validation(self):
        _, _, patient_admission_page = self._login_and_open_patient_admission()

        patient_admission_page.fill_patient_id("1" * 31)
        patient_admission_page.click_confirm()

        assert patient_admission_page.verify_validation_message("Patient ID can have up to 30 characters"), (
            "Expected validation message for Patient ID length > 30 characters."
        )

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_first_name_max_length_validation(self):
        _, _, patient_admission_page = self._login_and_open_patient_admission()

        patient_admission_page.fill_first_name("A" * 31)
        patient_admission_page.click_confirm()

        assert patient_admission_page.verify_validation_message("First name can have up to 30 characters"), (
            "Expected validation message for First Name length > 30 characters."
        )

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_last_name_max_length_validation(self):
        _, _, admission = self._login_and_open_patient_admission()

        admission.fill_last_name("L" * 31)
        admission.click_confirm()

        assert admission.verify_validation_message("Last name can have up to 30 characters")

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_first_name_special_characters_validation(self):
        _, _, admission = self._login_and_open_patient_admission()

        admission.fill_first_name("N@me123")
        admission.click_confirm()

        assert admission.verify_validation_message(
            "First name can not include special characters or numbers"
        )

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_last_name_special_characters_validation(self):
        _, _, admission = self._login_and_open_patient_admission()

        admission.fill_last_name("L@st123")
        admission.click_confirm()

        assert admission.verify_validation_message(
            "Last name can not include special characters or numbers"
        )

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_patient_id_special_characters_validation(self):
        _, _, admission = self._login_and_open_patient_admission()

        admission.fill_patient_id("ID@123")
        admission.click_confirm()

        assert admission.verify_validation_message(
            "Patient ID can only contain numbers and letters"
        )

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_patient_id_required_validation(self):
        _, _, admission = self._login_and_open_patient_admission()

        admission.clear_patient_id()
        admission.click_confirm()

        assert admission.verify_validation_message("Patient ID is required")

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_device_id_required_validation(self):
        _, _, admission = self._login_and_open_patient_admission()

        admission.clear_device_id()
        admission.click_confirm()

        assert admission.verify_validation_message("Device ID is required")

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_device_id_min_length_validation(self):
        _, _, admission = self._login_and_open_patient_admission()

        admission.fill_device_id("123")
        admission.click_confirm()

        assert admission.verify_validation_message("Device ID must be at least 4 characters")

    @pytest.mark.usefixtures("before_after_test")
    def test_patient_admission_device_not_activated_or_missing_validation(self):
        _, _, admission = self._login_and_open_patient_admission()
        patient_id = admission.get_patient_id_value() or "12345678"
        inactive_device_id = INACTIVE_DEVICE_ID

        admission.fill_patient_id(patient_id)
        admission.fill_device_id(inactive_device_id)
        admission.select_gender_male()
        admission.select_weight_unit_kg()
        admission.select_height_unit_cm()
        admission.fill_weight("80")
        admission.fill_height_cm("170")
        admission.select_first_referring_physician()
        admission.click_confirm()
        admission.fill_confirm_popup_patient_id(patient_id)
        admission.click_confirm_popup_confirm()

        try:
            admission.pw_page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        admission.pw_page.wait_for_timeout(500)

        expected_errors = [
            INACTIVE_DEVICE_ID_ERROR,
            "Device is not activated or does not exist.",
            "does not exist",
        ]
        error_found = False
        for _ in range(8):
            if any(admission.verify_error_message(msg) for msg in expected_errors):
                error_found = True
                break
            admission.pw_page.wait_for_timeout(500)

        assert error_found, "Expected inactive/missing device validation error was not displayed."

    # @pytest.mark.usefixtures("before_after_test")
    # def test_patient_admission_used_device_id_validation(self):
    #     if not USED_DEVICE_ID:
    #         pytest.skip("Set USED_DEVICE_ID env var to a known existing device id.")

    #     _, _, admission = self._login_and_open_patient_admission()

    #     admission.fill_device_id(USED_DEVICE_ID)
    #     admission.click_confirm()

    #     assert admission.verify_error_message(USED_DEVICE_ID_ERROR)

    @pytest.mark.parametrize("value", ["0", "9", "251", "600", "-10"])
    @pytest.mark.usefixtures("before_after_test")
    def test_invalid_weight_values(self, value):
        _, _, page = self._login_and_open_patient_admission()

        page.select_weight_unit_kg()
        page.fill_weight(value)
        page.click_confirm()

        expected_errors = [
            "Weight must be between 10-250 kg",
            "Weight must be between 10-250",
            "10-250 kg",
        ]
        assert any(page.verify_error_message(msg) for msg in expected_errors), (
            "Expected metric weight range validation message (10-250 kg)."
        )

    @pytest.mark.parametrize(
        "feet,inches,expected_message",
        [
            ("0", "0", "Feet must be between 1-7"),
            ("8", "0", "Feet must be between 1-7"),
            ("5", "-1", "Inches must be between 0-11"),
            ("5", "12", "Inches must be between 0-11"),
        ],
    )
    @pytest.mark.usefixtures("before_after_test")
    def test_invalid_height_values(self, feet, inches, expected_message):
        _, _, page = self._login_and_open_patient_admission()

        page.fill_height(feet, inches)
        page.click_confirm()

        assert page.verify_error_message(expected_message)