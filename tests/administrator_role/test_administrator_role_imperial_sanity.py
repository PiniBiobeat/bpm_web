import os
import pytest
import time
from typing import Tuple

from infra.config.config_provider import configuration
from logic.pages.login_page import LogInOnline
from logic.pages.patient_admission_page import PatientAdmissionPage
from logic.pages.session_management_page import SessionManagementPage
from tests.test_base_online import TestBaseOnline


SESSION_URL_FRAGMENT = "session-management"
ADMIN_EMAIL = os.getenv("ADMIN_IMPERIAL_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_IMPERIAL_PASSWORD")
SANITY_DEVICE_ID = "130646"


class TestAdministratorRoleImperialSanity(TestBaseOnline):
	def _fill_minimum_required_fields(self, admission: PatientAdmissionPage) -> str:
		# Minimum valid values for required fields only.
		patient_id = f"A{int(time.time()) % 10}"
		device_id = SANITY_DEVICE_ID

		admission.fill_patient_id(patient_id)
		admission.fill_device_id(device_id)
		admission.select_gender_male()
		admission.fill_weight("22")
		admission.fill_height("1", "0")
		admission.select_first_referring_physician()
		return patient_id

	def _confirm_admission_and_verify_redirect_overlay(self, admission: PatientAdmissionPage, patient_id: str):
		admission.click_confirm()
		popup_header = admission.pw_page.get_by_text(
			"Please confirm the patient ID to complete the admission process", exact=False
		).first
		popup_header.wait_for(state="visible", timeout=10000)

		admission.fill_confirm_popup_patient_id(patient_id)
		admission.click_confirm_popup_confirm()

		session_page = SessionManagementPage(admission.pw_page)
		assert session_page.verify_redirect_overlay_visible(), (
			"Expected redirect overlay text: 'You are being redirected to the Session Management screen'."
		)

	def _open_login_page(self) -> LogInOnline:
		page: LogInOnline = self.browser_online.navigate(configuration["online_url"], LogInOnline)
		assert page.verify_login_page_opened(), "Login page did not load for administrator scenario."
		return page

	def _login_to_session_management(self, page: LogInOnline) -> SessionManagementPage:
		page.login(ADMIN_EMAIL, ADMIN_PASSWORD)

		session_page = SessionManagementPage(page.pw_page)
		assert session_page.verify_session_management_page_opened(), (
			"Session management page did not load after administrator login."
		)
		assert session_page.verify_session_grid_opened(), (
			"Session grid controls or columns are not visible on session management page."
		)
		return session_page

	def _open_patient_admission(
		self, session_page: SessionManagementPage
	) -> PatientAdmissionPage:
		patient_admission_page: PatientAdmissionPage = session_page.open_patient_admission()
		assert patient_admission_page.verify_opened(), (
			"Patient admission form did not open with required fields and confirm action. "
			f"Details: {patient_admission_page.get_last_open_failure()}"
		)
		return patient_admission_page

	def _login_and_open_patient_admission(
		self,
	) -> Tuple[LogInOnline, SessionManagementPage, PatientAdmissionPage]:
		page = self._open_login_page()
		session_page = self._login_to_session_management(page)
		patient_admission_page = self._open_patient_admission(session_page)
		return page, session_page, patient_admission_page

	@pytest.mark.smoke
	@pytest.mark.usefixtures("before_after_test")
	def test_administrator_metric_user_admit_new_patient_sanity(self):
		page = self._open_login_page()
		try:
			session_page = self._login_to_session_management(page)
			admission = self._open_patient_admission(session_page)

			patient_id = self._fill_minimum_required_fields(admission)
			self._confirm_admission_and_verify_redirect_overlay(admission, patient_id)

			session_page = SessionManagementPage(page.pw_page)
			assert session_page.verify_session_management_page_opened(), (
				"Expected to be redirected to Session Management after successful patient assignment."
			)
			assert session_page.verify_patient_status_in_table(patient_id, "Pending"), (
				f"Expected admitted patient '{patient_id}' to appear in session table with status 'Pending'."
			)

			assert "patient-admission" in page.pw_page.url or SESSION_URL_FRAGMENT in page.pw_page.url, (
				f"Expected redirect to patient admission/session management, got '{page.pw_page.url}'"
			)
		finally:
			try:
				cleanup_session_page = SessionManagementPage(page.pw_page)
				cleanup_session_page.remove_session_by_device_id_if_exists(SANITY_DEVICE_ID)
			except Exception:
				pass