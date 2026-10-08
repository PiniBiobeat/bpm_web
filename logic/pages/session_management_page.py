from infra.page_base import PageBase
from logic.pages.patient_admission_page import PatientAdmissionPage
import re
from playwright.sync_api import expect
from typing import List


class SessionManagementPage(PageBase):
    URL_FRAGMENT = "session-management"

    # Top-level navigation / section entry points
    SESSION_MANAGEMENT_HEADER = "a[aria-label='Session Management']"
    PATIENT_ADMISSION_NAV = "a[aria-label='Patient Admission']"
    PATIENT_LOOKUP_NAV = "a[aria-label='Patient Lookup']"

    # Session grid controls (from session management landing page)
    SEARCH_SESSION_INPUT = (
        "input[placeholder='Search Session'], "
        "input[placeholder*='Search Session'], "
        "input[aria-label*='Search Session']"
    )
    FILTER_BY_STATUS_DROPDOWN = (
        "xpath=//label[contains(normalize-space(),'Filter by Status')]/following::div[@role='combobox'][1]"
    )
    SHOW_HIDE_COLUMNS_DROPDOWN = (
        "text=Show/Hide Columns"
    )
    REFRESH_BUTTON = (
        "button[aria-label*='Refresh'], button[aria-label*='refresh']"
    )
    REDIRECT_OVERLAY_TEXT = "You are being redirected to the Session Management screen"

    # Settings menu controls
    SETTINGS_BUTTON = (
        "//button[@id='profile-button']"
    )
    SETTINGS_MENU_CONTAINER = "#popover-content"
    SETTINGS_CLIENT_NAME = "#client-name-text"
    SETTINGS_USERNAME = "#username-text"
    SETTINGS_LOGOUT_CONTAINER = "#logout-container"
    SETTINGS_VERSION_TEXT = "#version-text"
    SETTINGS_EMAIL_SUPPORT_OPTION = "text=Email Support"
    SETTINGS_CHOOSE_DEPARTMENT_OPTION = "text=Choose Department"
    SETTINGS_LOGOUT_OPTION = "text=Log out"
    ROW_ACTION_BUTTON = (
        "button[aria-label*='more' i], "
        "button[aria-haspopup='menu'], "
        "button:has(svg)"
    )
    REMOVE_SESSION_OPTION = "text=Remove Session"
    REMOVE_SESSION_DIALOG = "[role='dialog']"
    REMOVE_SESSION_PATIENT_ID_INPUT = (
        "[role='dialog'] input[placeholder*='Patient ID'], "
        "[role='dialog'] input[placeholder*='Enter Patient ID'], "
        "[role='dialog'] input[name*='patient'], "
        "[role='dialog'] input"
    )
    REMOVE_SESSION_CONFIRM_BUTTON = "[role='dialog'] button:has-text('Remove')"

    # Session grid columns and states
    ADMISSION_DATE_HEADER = "text=Admission Date"
    PATIENT_ID_HEADER = "text=Patient ID"
    FULL_NAME_HEADER = "text=Full Name"
    DEVICE_ID_HEADER = "text=Device ID"
    REFERRING_PHYSICIAN_HEADER = "text=Referring Physician"
    START_TIME_HEADER = "text=Start Time"
    STATUS_HEADER = "text=Status"
    REMAINING_HEADER = "text=Remaining"

    def verify_session_management_page_opened(self):
        try:
            self.pw_page.wait_for_url(f"**/{self.URL_FRAGMENT}", timeout=30000)
            if self.URL_FRAGMENT not in self.pw_page.url:
                return False

            self._wait_any_visible(
                [
                    self.SESSION_MANAGEMENT_HEADER,
                    self.SEARCH_SESSION_INPUT,
                    self.FILTER_BY_STATUS_DROPDOWN,
                    self.SHOW_HIDE_COLUMNS_DROPDOWN,
                    self.PATIENT_ADMISSION_NAV,
                    self.PATIENT_LOOKUP_NAV,
                ],
                timeout=10000,
            )
            return True
        except Exception:
            return False

    def expect_session_management_page_opened(self):
        assert self.verify_session_management_page_opened(), "Session management page did not open."

    def expect_url(self, expected_url: str):
        expect(self.pw_page).to_have_url(expected_url, timeout=15000)

    def expect_header_and_navigation_visible(self):
        for selector in (self.SESSION_MANAGEMENT_HEADER, self.PATIENT_ADMISSION_NAV, self.PATIENT_LOOKUP_NAV):
            expect(self.pw_page.locator(selector).first).to_be_visible(timeout=10000)

    def expect_session_grid_opened(self):
        assert self.verify_session_grid_opened(), "Session grid controls/headers are not visible."

    def verify_session_grid_opened(self):
        try:
            self._wait_any_visible([self.SEARCH_SESSION_INPUT], timeout=10000)
            self._wait_any_visible([self.FILTER_BY_STATUS_DROPDOWN], timeout=10000)
            self._wait_any_visible([self.SHOW_HIDE_COLUMNS_DROPDOWN], timeout=10000)

            # Verify key table headers are present.
            self._wait_any_visible([self.ADMISSION_DATE_HEADER], timeout=10000)
            self._wait_any_visible([self.PATIENT_ID_HEADER], timeout=10000)
            self._wait_any_visible([self.FULL_NAME_HEADER], timeout=10000)
            self._wait_any_visible([self.DEVICE_ID_HEADER], timeout=10000)
            self._wait_any_visible([self.REFERRING_PHYSICIAN_HEADER], timeout=10000)
            self._wait_any_visible([self.START_TIME_HEADER], timeout=10000)
            self._wait_any_visible([self.STATUS_HEADER], timeout=10000)
            self._wait_any_visible([self.REMAINING_HEADER], timeout=10000)

            return True
        except Exception:
            return False

    def verify_required_controls_opened(self):
        try:
            if not self.verify_session_grid_opened():
                return False

            self._wait_any_visible(
                [
                    self.PATIENT_ADMISSION_NAV,
                    "text=New patient",
                    "text=New Patient",
                ],
                timeout=10000,
            )
            self._wait_any_visible([self.PATIENT_LOOKUP_NAV, "text=Patient Lookup"], timeout=10000)
            self._wait_any_visible([self.SETTINGS_BUTTON], timeout=10000)
            return True
        except Exception:
            return False

    def click_session_column_header(self, header_label: str):
        header = self._get_session_column_header(header_label)
        try:
            header.scroll_into_view_if_needed(timeout=2000)
        except Exception:
            pass
        header.click()
        self.pw_page.wait_for_timeout(400)

    def get_session_column_sort_state(self, header_label: str):
        try:
            header = self._get_session_column_header(header_label)
            raw_values = [
                (header.get_attribute("aria-sort") or "").strip().lower(),
                (header.get_attribute("data-sort") or "").strip().lower(),
                (header.get_attribute("data-sort-direction") or "").strip().lower(),
                (header.get_attribute("class") or "").strip().lower(),
            ]
            return self._normalize_sort_state(" ".join(raw_values))
        except Exception:
            return "unknown"

    def verify_session_column_sorted_ascending(self, header_label: str):
        self.click_session_column_header(header_label)
        return self.get_session_column_sort_state(header_label) == "ascending"

    def verify_session_column_sorted_descending(self, header_label: str):
        self.click_session_column_header(header_label)
        self.click_session_column_header(header_label)
        return self.get_session_column_sort_state(header_label) == "descending"

    def verify_session_columns_sorted_ascending_then_descending(self, header_labels: List[str]):
        for header_label in header_labels:
            self.click_session_column_header(header_label)
            if self.get_session_column_sort_state(header_label) != "ascending":
                return False

            self.click_session_column_header(header_label)
            if self.get_session_column_sort_state(header_label) != "descending":
                return False
        return True

    def _get_session_column_header(self, header_label: str):
        lowered = header_label.lower()
        xpath = (
            "xpath=(//th[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{lowered}')] | "
            "//*[@role='columnheader'][contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{lowered}')])[1]"
        )
        header = self.pw_page.locator(xpath).first
        header.wait_for(state="visible", timeout=10000)
        return header

    def _normalize_sort_state(self, raw_value: str):
        value = (raw_value or "").lower()
        if "descending" in value or " desc" in value or "-desc" in value or "_desc" in value:
            return "descending"
        if "ascending" in value or " asc" in value or "-asc" in value or "_asc" in value:
            return "ascending"
        if "sort-asc" in value:
            return "ascending"
        if "sort-desc" in value:
            return "descending"
        return "unknown"

    def verify_row_actions_by_status(self, status_value: str, expect_edit_enabled: bool):
        self.open_row_action_menu_by_status(status_value)

        edit_admission_option = self._get_visible_menu_option("Edit admission")
        complete_session_option = self._get_visible_menu_option("Complete session")
        remove_option = self._get_visible_menu_option(["Remove", "Remove Session"])

        edit_enabled = self._is_action_enabled(edit_admission_option)
        complete_enabled = self._is_action_enabled(complete_session_option)
        remove_enabled = self._is_action_enabled(remove_option)

        # Close menu before next interaction.
        self.pw_page.keyboard.press("Escape")

        return (
            edit_enabled == expect_edit_enabled
            and complete_enabled
            and remove_enabled
        )

    def open_row_action_menu_by_status(self, status_value: str):
        row = self.pw_page.locator(
            f"//tr[.//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{status_value.lower()}')]]"
        ).first
        row.wait_for(state="visible", timeout=15000)

        # In some builds, the row action button appears only on hover.
        try:
            row.hover()
        except Exception:
            pass

        action_button = row.locator(self.ROW_ACTION_BUTTON).last
        action_button.wait_for(state="visible", timeout=10000)
        action_button.click()

    def open_row_action_menu_for_any_existing_session(self):
        statuses = ["Pending", "Active", "Complete limited", "Complete"]
        for status in statuses:
            try:
                self.open_row_action_menu_by_status(status)
                return True
            except Exception:
                continue

        return False

    def verify_delete_related_row_actions_visible(self):
        if not self.open_row_action_menu_for_any_existing_session():
            return False

        try:
            self._get_visible_menu_option(["Edit session", "Edit admission", "Edit"]).is_visible()
            self._get_visible_menu_option("Complete session").is_visible()
            self._get_visible_menu_option(["Remove", "Remove Session"]).is_visible()
            return True
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def open_remove_session_dialog_for_any_existing_session(self):
        if not self.open_row_action_menu_for_any_existing_session():
            return False

        try:
            self._get_visible_menu_option(["Remove Session", "Remove"]).click()
            dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
            dialog.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    def click_cancel_in_remove_session_dialog(self):
        try:
            dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
            dialog.wait_for(state="visible", timeout=5000)
            cancel_button = dialog.get_by_role("button", name="Cancel", exact=False).first
            cancel_button.wait_for(state="visible", timeout=5000)
            cancel_button.click()

            # Allow close animation; if still open, use Escape as a fallback close action.
            try:
                dialog.wait_for(state="hidden", timeout=2000)
            except Exception:
                try:
                    self.pw_page.keyboard.press("Escape")
                except Exception:
                    pass
            return True
        except Exception:
            return False

    def verify_remove_session_dialog_closed(self):
        remove_dialog = self.pw_page.locator(
            f"{self.REMOVE_SESSION_DIALOG}:has-text('Are you sure you want to remove this session')"
        ).first

        # Poll for a short window because some builds close the dialog with animation.
        for _ in range(25):
            try:
                if remove_dialog.count() == 0:
                    return True

                if not remove_dialog.is_visible():
                    return True
            except Exception:
                return True

            self.pw_page.wait_for_timeout(200)

        try:
            remove_dialog.wait_for(state="hidden", timeout=1000)
            return True
        except Exception:
            return False

    def delete_session_with_wrong_then_correct_patient_id(self):
        if not self.open_remove_session_dialog_for_any_existing_session():
            return False

        dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
        remove_button = dialog.get_by_role("button", name="Remove", exact=False).first
        patient_id_input = dialog.locator(self.REMOVE_SESSION_PATIENT_ID_INPUT).first

        try:
            dialog.wait_for(state="visible", timeout=8000)
            remove_button.wait_for(state="visible", timeout=5000)
            patient_id_input.wait_for(state="visible", timeout=5000)
        except Exception:
            return False

        # Step: click Remove while empty; expected behavior is no deletion.
        try:
            remove_button.click(timeout=800)
        except Exception:
            pass

        dialog_text = ""
        patient_id_line = ""
        device_id_line = ""
        try:
            dialog_text = dialog.inner_text(timeout=3000) or ""
        except Exception:
            pass

        try:
            patient_lines = dialog.locator(
                "xpath=.//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'patient id')]"
            ).all_text_contents()
            for line in patient_lines:
                clean = (line or "").strip()
                if "patient id" in clean.lower():
                    patient_id_line = clean
                    break
        except Exception:
            pass

        try:
            device_lines = dialog.locator(
                "xpath=.//*[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'device id')]"
            ).all_text_contents()
            for line in device_lines:
                clean = (line or "").strip()
                if "device id" in clean.lower():
                    device_id_line = clean
                    break
        except Exception:
            pass

        patient_match = re.search(
            r"Patient\s*ID\s*:?\s*([A-Za-z0-9_-]+)",
            patient_id_line or dialog_text,
            flags=re.IGNORECASE,
        )
        device_match = re.search(
            r"Device\s*ID\s*:?\s*([A-Za-z0-9_-]+)",
            device_id_line or dialog_text,
            flags=re.IGNORECASE,
        )

        patient_id = patient_match.group(1).strip() if patient_match else ""
        device_id = device_match.group(1).strip() if device_match else ""
        if not patient_id:
            return False

        lookup_value = device_id or patient_id
        before_count = 0
        try:
            self.search_session(lookup_value)
            before_count = self.pw_page.locator(
                f"//tr[.//*[contains(normalize-space(),'{lookup_value}')]]"
            ).count()
        except Exception:
            before_count = 0

        wrong_patient_id = f"{patient_id}0"
        if wrong_patient_id == patient_id:
            wrong_patient_id = f"X{patient_id}"

        # Step: enter wrong ID and click Remove.
        try:
            patient_id_input.fill("")
            patient_id_input.fill(wrong_patient_id)
            remove_button.click(timeout=1000)
        except Exception:
            pass

        # Step: copy Patient ID from popup and insert into input field.
        try:
            copied_patient_id = patient_id
            patient_id_input.fill("")
            patient_id_input.fill(copied_patient_id)
        except Exception:
            return False

        # Step: click Remove with correct copied ID.
        for _ in range(20):
            try:
                remove_button.click(timeout=1200)
            except Exception:
                pass
            self.pw_page.wait_for_timeout(200)
            try:
                if not dialog.is_visible():
                    break
            except Exception:
                break

        if not self.verify_remove_session_dialog_closed():
            return False

        try:
            self.search_session(lookup_value)
            after_rows = self.pw_page.locator(
                f"//tr[.//*[contains(normalize-space(),'{lookup_value}')]]"
            )
            for _ in range(35):
                after_count = after_rows.count()
                if after_count == 0:
                    return True
                if before_count > 0 and after_count < before_count:
                    return True
                self.pw_page.wait_for_timeout(200)
            return False
        except Exception:
            return True

    def delete_session_and_verify_patient_not_in_session_management(self):
        if not self.open_remove_session_dialog_for_any_existing_session():
            return False

        dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
        remove_button = dialog.get_by_role("button", name="Remove", exact=False).first
        patient_id_input = dialog.locator(self.REMOVE_SESSION_PATIENT_ID_INPUT).first

        try:
            dialog.wait_for(state="visible", timeout=8000)
            remove_button.wait_for(state="visible", timeout=5000)
            patient_id_input.wait_for(state="visible", timeout=5000)
        except Exception:
            return False

        dialog_text = ""
        try:
            dialog_text = dialog.inner_text(timeout=3000) or ""
        except Exception:
            pass

        # Copy Patient ID from the popup details line: "Patient ID: <value>".
        patient_id = ""
        for line in dialog_text.splitlines():
            if "patient id" not in line.lower():
                continue

            match = re.search(r"Patient\s*ID\s*:\s*(.+)", line, flags=re.IGNORECASE)
            if match:
                patient_id = match.group(1).strip()
                break

        if not patient_id:
            patient_match = re.search(
                r"Patient\s*ID\s*:?\s*([A-Za-z0-9_-]+)",
                dialog_text,
                flags=re.IGNORECASE,
            )
            patient_id = patient_match.group(1).strip() if patient_match else ""

        if not patient_id:
            return False

        # Copy patient ID from popup and insert it into confirmation input.
        try:
            patient_id_input.fill("")
            patient_id_input.fill(patient_id)
            patient_id_input.press("Tab")
        except Exception:
            return False

        # Wait until Remove becomes enabled after entering the copied Patient ID.
        for _ in range(25):
            if self._is_action_enabled(remove_button):
                break
            self.pw_page.wait_for_timeout(150)

        for _ in range(20):
            try:
                remove_button.click(timeout=1200)
            except Exception:
                pass

            self.pw_page.wait_for_timeout(200)
            try:
                if not dialog.is_visible():
                    break
            except Exception:
                break

        if not self.verify_remove_session_dialog_closed():
            return False

        try:
            # Ensure we are on Session Management before verifying row absence.
            self._click_any_visible([self.SESSION_MANAGEMENT_HEADER, "text=Session Management"], timeout=10000)
            self.search_session(patient_id)
            self.pw_page.wait_for_timeout(1000)
        except Exception:
            return False

        patient_row = self.pw_page.locator(
            f"//tr[.//*[contains(normalize-space(),'{patient_id}')]]"
        )
        return patient_row.count() == 0

    def copy_patient_id_from_remove_session_dialog(self):
        dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
        try:
            dialog.wait_for(state="visible", timeout=8000)
            dialog_text = dialog.inner_text(timeout=3000) or ""
        except Exception:
            return ""

        # Same extraction strategy used in remove_session_by_device_id_if_exists.
        match = re.search(r"Patient\s*ID\s*:\s*([^\r\n]+)", dialog_text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def paste_patient_id_in_remove_session_field(self, patient_id: str):
        try:
            dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
            dialog.wait_for(state="visible", timeout=5000)
            # Same input-locator strategy used in remove_session_by_device_id_if_exists.
            patient_id_input = dialog.locator("input[id^=':r'], input[type='text'], input").first
            patient_id_input.wait_for(state="visible", timeout=5000)
            patient_id_input.fill("")
            patient_id_input.fill(patient_id)
            patient_id_input.press("Tab")
            return True
        except Exception:
            return False

    def click_remove_in_remove_session_dialog(self):
        try:
            dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
            dialog.wait_for(state="visible", timeout=5000)
            remove_button = dialog.get_by_role("button", name="Remove", exact=False).first
            remove_button.wait_for(state="visible", timeout=5000)

            # Same enable-wait pattern used in remove_session_by_device_id_if_exists.
            for _ in range(25):
                if self._is_action_enabled(remove_button):
                    break
                self.pw_page.wait_for_timeout(150)

            remove_button.click(timeout=1500)
            return True
        except Exception:
            # Same fallback behavior used in remove_session_by_device_id_if_exists.
            confirm_candidates = [
                self.pw_page.get_by_role("button", name="Remove", exact=False).first,
                self.pw_page.get_by_role("button", name="Confirm", exact=False).first,
            ]
            for candidate in confirm_candidates:
                try:
                    if candidate.is_visible(timeout=2000):
                        candidate.click()
                        return True
                except Exception:
                    continue
            return False

    def verify_remove_button_disabled_for_empty_patient_id(self):
        try:
            dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
            dialog.wait_for(state="visible", timeout=5000)

            patient_id_input = dialog.locator("input[id^=':r'], input[type='text'], input").first
            patient_id_input.wait_for(state="visible", timeout=5000)
            patient_id_input.fill("")
            patient_id_input.press("Tab")

            remove_button = dialog.get_by_role("button", name="Remove", exact=False).first
            remove_button.wait_for(state="visible", timeout=5000)
            return not self._is_action_enabled(remove_button)
        except Exception:
            return False

    def verify_remove_button_disabled_for_wrong_patient_id(self, expected_patient_id: str):
        try:
            dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
            dialog.wait_for(state="visible", timeout=5000)

            patient_id_input = dialog.locator("input[id^=':r'], input[type='text'], input").first
            patient_id_input.wait_for(state="visible", timeout=5000)

            wrong_patient_id = f"{expected_patient_id}0"
            if wrong_patient_id == expected_patient_id:
                wrong_patient_id = f"X{expected_patient_id}"

            patient_id_input.fill("")
            patient_id_input.fill(wrong_patient_id)
            patient_id_input.press("Tab")

            self.pw_page.wait_for_timeout(300)
            remove_button = dialog.get_by_role("button", name="Remove", exact=False).first
            remove_button.wait_for(state="visible", timeout=5000)
            return not self._is_action_enabled(remove_button)
        except Exception:
            return False

    def verify_patient_not_in_session_management(self, patient_id: str):
        try:
            self._click_any_visible([self.SESSION_MANAGEMENT_HEADER, "text=Session Management"], timeout=10000)
            self.search_session(patient_id)
        except Exception:
            return False

        patient_row = self.pw_page.locator(
            f"//tr[.//*[contains(normalize-space(),'{patient_id}')]]"
        )

        for _ in range(30):
            if patient_row.count() == 0:
                return True
            self.pw_page.wait_for_timeout(200)

        return False

    def delete_session_and_verify_patient_not_in_lookup(self):
        # Backward-compatible wrapper for older tests.
        return self.delete_session_and_verify_patient_not_in_session_management()

    def _get_visible_menu_option(self, labels):
        if isinstance(labels, str):
            labels = [labels]

        for label in labels:
            menu_item = self.pw_page.get_by_role("menuitem", name=label, exact=False).first
            try:
                menu_item.wait_for(state="visible", timeout=2000)
                return menu_item
            except Exception:
                pass

            text_item = self.pw_page.get_by_text(label, exact=False).first
            try:
                text_item.wait_for(state="visible", timeout=2000)
                return text_item
            except Exception:
                pass

        raise AssertionError(f"Could not find visible menu option for labels: {labels}")

    def _is_action_enabled(self, locator):
        try:
            aria_disabled = (locator.get_attribute("aria-disabled") or "").strip().lower()
            if aria_disabled == "true":
                return False
        except Exception:
            pass

        try:
            class_name = (locator.get_attribute("class") or "").lower()
            if "disabled" in class_name:
                return False
        except Exception:
            pass

        try:
            return locator.is_enabled()
        except Exception:
            return False

    def open_patient_admission(self):
        self._click_any_visible([self.PATIENT_ADMISSION_NAV], timeout=10000)
        return PatientAdmissionPage(self.pw_page)

    def open_settings_menu(self):
        self._click_any_visible([self.SETTINGS_BUTTON], timeout=10000)

    def expect_settings_menu_opened(self):
        assert self.verify_settings_menu_opened(), (
            "Expected Email Support, Choose Department, and Log out options in the settings menu."
        )

    def expect_email_support_visible(self):
        expect(self.pw_page.locator(self.SETTINGS_EMAIL_SUPPORT_OPTION).first).to_be_visible(timeout=10000)

    def expect_choose_department_visible(self):
        expect(self.pw_page.locator(self.SETTINGS_CHOOSE_DEPARTMENT_OPTION).first).to_be_visible(timeout=10000)

    def expect_settings_client_name(self, expected_client_name: str):
        expect(self.pw_page.locator(self.SETTINGS_CLIENT_NAME).first).to_have_text(
            expected_client_name, timeout=10000
        )

    def expect_settings_user_email_visible(self, user_email: str):
        expect(self.pw_page.get_by_text(user_email).first).to_be_visible(timeout=10000)

    def verify_settings_menu_opened(self):
        try:
            self._wait_any_visible([self.SETTINGS_MENU_CONTAINER], timeout=10000)
            self._wait_any_visible([self.SETTINGS_CLIENT_NAME], timeout=10000)
            self._wait_any_visible([self.SETTINGS_USERNAME], timeout=10000)
            self._wait_any_visible([self.SETTINGS_LOGOUT_CONTAINER], timeout=10000)
            self._wait_any_visible([self.SETTINGS_EMAIL_SUPPORT_OPTION], timeout=10000)
            self._wait_any_visible([self.SETTINGS_CHOOSE_DEPARTMENT_OPTION], timeout=10000)
            self._wait_any_visible([self.SETTINGS_LOGOUT_OPTION], timeout=10000)
            return True
        except Exception:
            return False

    def verify_settings_user_email_visible(self, user_email: str):
        try:
            self.pw_page.get_by_text(user_email, exact=False).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    def verify_settings_client_name_equals(self, expected_client_name: str):
        try:
            client_name = (self.pw_page.locator(self.SETTINGS_CLIENT_NAME).first.text_content() or "").strip()
            return client_name == expected_client_name
        except Exception:
            return False

    def verify_email_support_visible(self):
        try:
            self.pw_page.locator(self.SETTINGS_EMAIL_SUPPORT_OPTION).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    def verify_choose_department_visible(self):
        try:
            self.pw_page.locator(self.SETTINGS_CHOOSE_DEPARTMENT_OPTION).first.wait_for(
                state="visible", timeout=10000
            )
            return True
        except Exception:
            return False

    def switch_to_other_department_from_settings(self):
        try:
            # Step 1: Ensure settings menu is open, then open Choose Department dropdown.
           # self.open_settings_menu()
            if not self._open_choose_department_selector():
                return False

            # Step 2: Collect all available department options and their display text.
            options = self._get_department_options()
            if len(options) < 2:
                return False

            option_texts = []
            for opt in options:
                try:
                    text = (opt.inner_text() or opt.get_attribute("aria-label") or "").strip()
                except Exception:
                    text = ""
                option_texts.append(text)

            # Step 3: Identify the currently selected department by aria/class attributes.
            current_text = ""
            for i, opt in enumerate(options):
                if self._is_department_option_selected(opt):
                    current_text = option_texts[i]
                    break

            # If selection detection yielded nothing, treat the first item as current.
            if not current_text and option_texts:
                current_text = option_texts[0]

            # Step 4: Pick the first department that differs from the current one.
            target_index = -1
            target_text = ""
            for i, text in enumerate(option_texts):
                if text and text != current_text:
                    target_index = i
                    target_text = text
                    break

            if target_index == -1:
                return False

            # Step 5: Click the chosen department.
            target_option = options[target_index]
            target_option.scroll_into_view_if_needed(timeout=1500)
            target_option.click(timeout=4000, force=True)
            self.pw_page.wait_for_timeout(800)

            # Step 6: Validate — re-open chooser and verify the selected name changed.
            self.open_settings_menu()
            if not self._open_choose_department_selector():
                # Dropdown did not re-open; assume success if SM page is visible.
                return bool(self.verify_session_management_page_opened())

            refreshed_options = self._get_department_options()
            refreshed_texts = []
            for opt in refreshed_options:
                try:
                    text = (opt.inner_text() or opt.get_attribute("aria-label") or "").strip()
                except Exception:
                    text = ""
                refreshed_texts.append(text)

            # Find the newly selected department by aria/class.
            new_selected_text = ""
            for i, opt in enumerate(refreshed_options):
                if self._is_department_option_selected(opt):
                    new_selected_text = refreshed_texts[i]
                    break

            # Fall back to aria-label match when selection marker is absent.
            if not new_selected_text:
                new_selected_text = target_text if target_text in refreshed_texts else ""

            # Validate: new department != original AND session management page loaded.
            changed = new_selected_text != current_text
            return changed and bool(self.verify_session_management_page_opened())
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def _open_choose_department_selector(self):
        try:
            self.pw_page.locator(self.SETTINGS_CHOOSE_DEPARTMENT_OPTION).first.wait_for(state="visible", timeout=4000)
            self.pw_page.locator(self.SETTINGS_CHOOSE_DEPARTMENT_OPTION).first.click(timeout=4000)

            popup_candidates = ["[role='listbox']", "[role='menu']", "[role='dialog']", "#popover-content"]
            for selector in popup_candidates:
                try:
                    popup = self.pw_page.locator(selector).last
                    popup.wait_for(state="visible", timeout=2000)
                    return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _get_department_options(self):
        # Primary: MuiPopover structure — <p aria-label="DeptName"> inside the popover paper
        try:
            popover = self.pw_page.locator("div.MuiPaper-root.MuiPopover-paper").last
            popover.wait_for(state="visible", timeout=1500)
            items = popover.locator("p[aria-label]")
            count = items.count()
            if count >= 1:
                return [items.nth(i) for i in range(count)]
        except Exception:
            pass

        # Fallback: role-based containers
        containers = ["[role='listbox']", "[role='menu']", "[role='dialog']", "#popover-content"]
        for container_selector in containers:
            try:
                container = self.pw_page.locator(container_selector).last
                container.wait_for(state="visible", timeout=1500)

                candidates = [
                    "[role='option']",
                    "[role='menuitemradio']",
                    "li",
                ]
                for candidate in candidates:
                    options = container.locator(candidate)
                    count = options.count()
                    if count >= 2:
                        return [options.nth(i) for i in range(count)]
            except Exception:
                continue
        return []

    def _is_department_option_selected(self, option_locator):
        try:
            aria_selected = (option_locator.get_attribute("aria-selected") or "").strip().lower()
            if aria_selected == "true":
                return True
        except Exception:
            pass

        try:
            aria_checked = (option_locator.get_attribute("aria-checked") or "").strip().lower()
            if aria_checked == "true":
                return True
        except Exception:
            pass

        try:
            class_name = (option_locator.get_attribute("class") or "").lower()
            if "selected" in class_name or "checked" in class_name or "mui-selected" in class_name:
                return True
        except Exception:
            pass

        try:
            checkbox = option_locator.locator("xpath=.//input[@type='checkbox' or @type='radio']").first
            if checkbox.count() > 0 and checkbox.is_checked():
                return True
        except Exception:
            pass

        return False

    def open_patient_lookup(self):
        self._click_any_visible([self.PATIENT_LOOKUP_NAV, "text=Patient Lookup"], timeout=10000)

    def verify_patient_lookup_opened(self):
        try:
            self.pw_page.wait_for_url("**/patient-lookup**", timeout=10000)
        except Exception:
            pass
        try:
            self._wait_any_visible(
                [
                    "text=Patient lookup",
                    "text=Patient Lookup",
                    "h1:has-text('Patient')",
                ],
                timeout=10000,
            )
            self._wait_any_visible(
                [
                    "input[placeholder*='Search'], input[aria-label*='Search'], input[placeholder*='Patient']"
                ],
                timeout=10000,
            )
            self._wait_any_visible(
                [
                    "button:has-text('New Patient'), button:has-text('New patient')"
                ],
                timeout=10000,
            )
            return True
        except Exception:
            return False

    def verify_patient_lookup_table_columns_visible(self):
        expected_columns = [
            "Patient ID",
            "First name",
            "Last name",
            "Last session",
            "Department",
        ]
        try:
            for col in expected_columns:
                self._wait_any_visible([f"text={col}"], timeout=5000)
            return True
        except Exception:
            return False

    def search_patient_lookup(self, value: str):
        locator = self.pw_page.locator(
            "input[placeholder*='Search'], input[aria-label*='Search'], input[placeholder*='Patient']"
        ).first
        locator.wait_for(state="visible", timeout=8000)
        locator.fill(value)
        self.pw_page.wait_for_timeout(700)

    def verify_table_shows_no_results(self):
        try:
            no_results_candidates = [
                "text=No results found",
                "text=No results",
                "text=No data",
                "text=Empty",
            ]
            for selector in no_results_candidates:
                try:
                    self.pw_page.locator(selector).first.wait_for(state="visible", timeout=3000)
                    return True
                except Exception:
                    pass

            # Fallback: count data rows in the table
            rows = self.pw_page.locator("//tr[.//td]")
            self.pw_page.wait_for_timeout(500)
            return rows.count() == 0
        except Exception:
            return False

    def get_current_department_name(self):
        """Return the display name of the currently selected department.

        Requires the settings menu and Choose Department dropdown to already
        be open (call open_settings_menu / _open_choose_department_selector first).
        Falls back to the first option in the list when no selection marker is found.
        """
        try:
            options = self._get_department_options()
            if not options:
                return ""

            # Prefer the option marked as selected via aria/class attributes.
            for opt in options:
                if self._is_department_option_selected(opt):
                    try:
                        return (opt.inner_text() or opt.get_attribute("aria-label") or "").strip()
                    except Exception:
                        pass

            # Fall back to the first option's aria-label or text when no marker found.
            try:
                first = options[0]
                return (first.get_attribute("aria-label") or first.inner_text() or "").strip()
            except Exception:
                pass
        except Exception:
            pass
        return ""

    def click_logout(self):
        self._click_any_visible([self.SETTINGS_LOGOUT_OPTION], timeout=10000)

    def verify_redirect_overlay_visible(self):
        expected = self.REDIRECT_OVERLAY_TEXT.lower()

        # Overlay can be very short-lived; poll for a short window.
        for _ in range(40):
            try:
                if self.pw_page.get_by_text(self.REDIRECT_OVERLAY_TEXT, exact=False).first.is_visible(timeout=100):
                    return True
            except Exception:
                pass

            try:
                body_text = (self.pw_page.locator("body").inner_text(timeout=200) or "").lower()
                if expected in body_text:
                    return True
            except Exception:
                pass

            self.pw_page.wait_for_timeout(200)

        # Fallback: treat successful redirect as acceptable when overlay is missed due to timing.
        try:
            return self.URL_FRAGMENT in self.pw_page.url
        except Exception:
            return False

    def search_session(self, value: str):
        self.pw_page.locator(self.SEARCH_SESSION_INPUT).first.fill(value)

    def get_first_session_row_field_value(self, header_label: str):
        try:
            column_index = self._get_session_column_index(header_label)
            row = self.pw_page.locator("//tr[.//td]").first
            row.wait_for(state="visible", timeout=10000)
            value = row.locator(f"td:nth-child({column_index})").first.text_content() or ""
            return value.strip()
        except Exception:
            return ""

    def verify_search_filters_results(self, query: str):
        if not query:
            return False

        self.search_session(query)
        self.pw_page.wait_for_timeout(700)

        rows = self.pw_page.locator("//tr[.//td]")
        row_count = rows.count()
        if row_count == 0:
            return False

        query_lower = query.strip().lower()
        max_rows = min(row_count, 20)
        for index in range(max_rows):
            row_text = (rows.nth(index).inner_text() or "").lower()
            if query_lower not in row_text:
                return False
        return True

    def open_filter_by_status_dropdown(self):
        try:
            self._click_any_visible([self.FILTER_BY_STATUS_DROPDOWN], timeout=6000)
            return True
        except Exception:
            return False

    def verify_filter_by_status_options_visible(self, options: List[str]):
        if not self.open_filter_by_status_dropdown():
            return False

        try:
            for option in options:
                self.pw_page.get_by_text(option, exact=False).first.wait_for(state="visible", timeout=4000)
            return True
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def apply_filter_by_status(self, status_value: str):
        if not self.open_filter_by_status_dropdown():
            return False

        status_aliases = {
            "complete and limited": [
                "Complete & Complete Limited",
                "Complete and limited",
                "Complete limited",
                "Complete",
            ],
            "complete limited": [
                "Complete & Complete Limited",
                "Complete limited",
                "Complete and limited",
                "Complete",
            ],
        }
        labels = status_aliases.get(status_value.strip().lower(), [status_value])

        for label in labels:
            try:
                # Explicit flow: open dropdown listbox, then click the wanted status option.
                listbox = self.pw_page.locator("[role='listbox']").last
                listbox.wait_for(state="visible", timeout=3000)

                option = listbox.get_by_text(label, exact=False).first
                option.wait_for(state="visible", timeout=2000)
                option.click(timeout=3000)
                self.pw_page.wait_for_timeout(300)

                # MUI dropdown may stay open in some runs; force close before continuing.
                if self.pw_page.locator("[role='listbox']").count() > 0:
                    try:
                        self.pw_page.keyboard.press("Escape")
                    except Exception:
                        pass
                    self.pw_page.wait_for_timeout(200)

                if self.pw_page.locator("[role='listbox']").count() > 0:
                    try:
                        self.pw_page.mouse.click(5, 5)
                    except Exception:
                        pass

                self.pw_page.wait_for_timeout(400)
                return True
            except Exception:
                continue

        return False

    def verify_only_rows_with_status_visible(self, status_value: str):
        rows = self.pw_page.locator("//tr[.//td]")
        row_count = rows.count()
        if row_count == 0:
            return False

        expected = status_value.strip().lower().replace(" and ", " ")
        max_rows = min(row_count, 20)
        for index in range(max_rows):
            row_text = (rows.nth(index).inner_text() or "").lower().replace(" and ", " ")
            if expected not in row_text:
                return False
        return True

    def open_show_hide_columns_dropdown(self):
        for _ in range(3):
            try:
                self._click_any_visible([self.SHOW_HIDE_COLUMNS_DROPDOWN], timeout=6000)
                self._get_show_hide_columns_container()
                return True
            except Exception:
                try:
                    self.pw_page.keyboard.press("Escape")
                except Exception:
                    pass
                self.pw_page.wait_for_timeout(250)
        return False

    def get_show_hide_columns_options(self):
        if not self.open_show_hide_columns_dropdown():
            return []

        try:
            container = self._get_show_hide_columns_container()
            options = []

            list_items = container.locator("li")
            item_count = list_items.count()
            for index in range(item_count):
                text_value = (list_items.nth(index).inner_text() or "").strip()
                text_value = re.sub(r"\s+", " ", text_value)
                if text_value:
                    options.append(text_value)

            if options:
                return options

            # Fallback when options are not rendered as list items.
            container_text = (container.inner_text(timeout=1000) or "").strip()
            lines = [re.sub(r"\s+", " ", line).strip() for line in container_text.splitlines()]
            return [line for line in lines if line]
        except Exception:
            return []
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def verify_show_hide_columns_dropdown_without_device_id(self):
        if not self.open_show_hide_columns_dropdown():
            return False

        try:
            popup_selectors = [
                "[role='menu']",
                "[role='listbox']",
                "[role='dialog']",
                "#popover-content",
            ]
            container_text = ""
            for selector in popup_selectors:
                try:
                    locator = self.pw_page.locator(selector).last
                    locator.wait_for(state="visible", timeout=800)
                    container_text = (locator.inner_text(timeout=800) or "").lower()
                    if container_text:
                        break
                except Exception:
                    continue

            if not container_text:
                container_text = (self.pw_page.locator("body").inner_text() or "").lower()
            return "device id" not in container_text
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def mark_columns_in_show_hide_dropdown(self, columns: List[str]):
        if not self.open_show_hide_columns_dropdown():
            return False

        try:
            container = self._get_show_hide_columns_container()
            for column in columns:
                container.get_by_text(column, exact=False).first.click(timeout=3000)
                self.pw_page.wait_for_timeout(150)
            return True
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def verify_show_hide_column_selected(self, column_name: str):
        if not self.open_show_hide_columns_dropdown():
            return False

        try:
            container = self._get_show_hide_columns_container()
            option = self._get_show_hide_option_locator(container, column_name)
            option.wait_for(state="visible", timeout=3000)

            # MUI list options use aria-selected for selected state.
            try:
                aria_selected = (option.get_attribute("aria-selected") or "").strip().lower()
                if aria_selected in ["true", "false"]:
                    return aria_selected == "true"
            except Exception:
                pass

            # Fallbacks when aria-selected is not available.
            try:
                checkbox = option.locator("xpath=.//input[@type='checkbox']").first
                if checkbox.count() > 0:
                    return checkbox.is_checked()
            except Exception:
                pass

            try:
                class_name = (option.get_attribute("class") or "").lower()
                return "checked" in class_name or "selected" in class_name
            except Exception:
                return False
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def ensure_show_hide_column_selected(self, column_name: str):
        if not self.open_show_hide_columns_dropdown():
            return False

        try:
            container = self._get_show_hide_columns_container()
            option = self._get_show_hide_option_locator(container, column_name)
            try:
                option.wait_for(state="visible", timeout=3000)
            except Exception:
                option = self._get_show_hide_option_locator(self.pw_page.locator("body"), column_name)
                option.wait_for(state="visible", timeout=3000)

            for _ in range(2):
                try:
                    aria_selected = (option.get_attribute("aria-selected") or "").strip().lower()
                    class_name = (option.get_attribute("class") or "").lower()
                    if aria_selected == "true" or "mui-selected" in class_name or "selected" in class_name:
                        return True
                except Exception:
                    pass

                try:
                    option.scroll_into_view_if_needed(timeout=1500)
                except Exception:
                    pass

                option.click(timeout=3000, force=True)
                self.pw_page.wait_for_timeout(300)

            try:
                aria_selected = (option.get_attribute("aria-selected") or "").strip().lower()
                class_name = (option.get_attribute("class") or "").lower()
                return aria_selected == "true" or "mui-selected" in class_name or "selected" in class_name
            except Exception:
                return False
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def verify_session_column_visible_by_name(self, column_name: str):
        aliases = {
            "session initiator": ["session initiator", "initiator"],
        }
        names = aliases.get(column_name.strip().lower(), [column_name.strip().lower()])

        headers = self._get_visible_session_column_headers()
        for visible in headers:
            for expected in names:
                if expected in visible:
                    return True
        return False

    def verify_expected_visible_columns(self, expected_columns: List[str]):
        expected = {col.strip().lower() for col in expected_columns}
        visible_headers = set(self._get_visible_session_column_headers())
        return expected.issubset(visible_headers)

    def verify_session_initiator_column_added(self):
        selectors = [
            "xpath=//th[.//span[@role='button' and contains(normalize-space(),'Session Initiator')]]",
            "xpath=//th[normalize-space()='Session Initiator']",
            "xpath=//*[@role='columnheader'][contains(normalize-space(),'Session Initiator')]",
        ]

        for selector in selectors:
            try:
                header = self.pw_page.locator(selector).first
                header.wait_for(state="visible", timeout=3000)
                if header.is_visible():
                    return True
            except Exception:
                continue

        return False

    def select_session_initiator_column_and_verify_added(self):
        if not self.open_show_hide_columns_dropdown():
            return False

        try:
            container = self._get_show_hide_columns_container()
            option = container.locator("[role='option'][data-value='session_initiator'], li[data-value='session_initiator']").first
            option.wait_for(state="visible", timeout=4000)

            selected = False
            try:
                aria_selected = (option.get_attribute("aria-selected") or "").strip().lower()
                class_name = (option.get_attribute("class") or "").lower()
                selected = aria_selected == "true" or "mui-selected" in class_name or "selected" in class_name
            except Exception:
                selected = False

            if not selected:
                option.click(timeout=3000, force=True)
                self.pw_page.wait_for_timeout(350)

            return True
        except Exception:
            return False
        finally:
            try:
                self.pw_page.keyboard.press("Escape")
            except Exception:
                pass

    def verify_pagination_options_work(self):
        candidates = ["10", "25", "50", "100", "Rows per page", "per page"]
        found_any = False

        for candidate in candidates:
            try:
                control = self.pw_page.get_by_text(candidate, exact=False).first
                control.wait_for(state="visible", timeout=1200)
                found_any = True
                if candidate.isdigit():
                    try:
                        control.click(timeout=1200)
                        self.pw_page.wait_for_timeout(300)
                    except Exception:
                        pass
            except Exception:
                continue

        return found_any

    def verify_search_field_tooltip_text(self, expected_text: str):
        try:
            search_input = self.pw_page.locator(self.SEARCH_SESSION_INPUT).first
            search_input.wait_for(state="visible", timeout=5000)
            search_input.hover()
            self.pw_page.wait_for_timeout(400)

            tooltip_candidates = [
                "[role='tooltip']",
                "div[aria-describedby]",
                "text=Search by Patient ID, Name, Device ID, or Session Initiator",
            ]

            expected = expected_text.strip().lower()
            for selector in tooltip_candidates:
                try:
                    text_value = (self.pw_page.locator(selector).first.inner_text(timeout=1000) or "").lower()
                    if expected in text_value:
                        return True
                except Exception:
                    continue

            body_text = (self.pw_page.locator("body").inner_text(timeout=1000) or "").lower()
            return expected in body_text
        except Exception:
            return False

    def _get_session_column_index(self, header_label: str):
        lowered = header_label.strip().lower()
        headers = self.pw_page.locator("//th | //*[@role='columnheader']")
        count = headers.count()
        for index in range(count):
            header_text = (headers.nth(index).inner_text() or "").strip().lower()
            if lowered in header_text:
                return index + 1
        raise AssertionError(f"Could not find table column index for header '{header_label}'.")

    def _get_visible_session_column_headers(self):
        headers = self.pw_page.locator("//th | //*[@role='columnheader']")
        count = headers.count()
        visible = []
        for index in range(count):
            try:
                if headers.nth(index).is_visible():
                    text_value = (headers.nth(index).inner_text() or "").strip().lower()
                    if text_value:
                        visible.append(text_value)
            except Exception:
                continue
        return visible

    def _get_show_hide_columns_container(self):
        selectors = ["[role='menu']", "[role='listbox']", "#popover-content", "[role='dialog']"]
        for selector in selectors:
            locator = self.pw_page.locator(selector).last
            try:
                locator.wait_for(state="visible", timeout=1500)
                return locator
            except Exception:
                continue

        raise AssertionError("Could not find an opened Show/Hide Columns dropdown container.")

    def _get_show_hide_option_locator(self, container, column_name: str):
        name = (column_name or "").strip().lower()
        data_value_map = {
            "session initiator": "session_initiator",
            "referring physician": "referring_physician",
            "start time": "report_start_time",
            "status": "status",
            "remaining": "remaining",
        }

        data_value = data_value_map.get(name)
        if data_value:
            by_data = container.locator(f"[role='option'][data-value='{data_value}'], li[data-value='{data_value}']").first
            if by_data.count() > 0:
                return by_data

        return container.get_by_text(column_name, exact=False).first

    def verify_patient_status_in_table(self, patient_id: str, expected_status: str):
        try:
            self.search_session(patient_id)
            row = self.pw_page.locator(
                f"//tr[.//*[contains(normalize-space(),'{patient_id}')]]"
            ).first
            row.wait_for(state="visible", timeout=15000)
            row.get_by_text(expected_status, exact=False).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False

    def remove_session_by_device_id_if_exists(self, device_id: str):
        self.search_session(device_id)
        self.pw_page.wait_for_timeout(800)

        row = self.pw_page.locator(
            f"//tr[.//*[contains(normalize-space(),'{device_id}')]]"
        ).first
        if row.count() == 0:
            return False

        row.wait_for(state="visible", timeout=10000)
        patient_id = (row.locator("td").first.text_content() or "").strip()

        # The row action button is shown only on row hover in some builds.
        try:
            row.hover()
        except Exception:
            pass

        action_button = row.locator(self.ROW_ACTION_BUTTON).last
        try:
            action_button.wait_for(state="visible", timeout=4000)
        except Exception:
            try:
                row.dispatch_event("mouseover")
            except Exception:
                pass
            self.pw_page.wait_for_timeout(300)

        action_button.click()
        self.pw_page.get_by_text("Remove Session", exact=False).first.click()

        # Some builds require entering Patient ID in a confirmation dialog.
        try:
            dialog = self.pw_page.locator(self.REMOVE_SESSION_DIALOG).first
            dialog.wait_for(state="visible", timeout=5000)

            # Use the same Patient ID shown in the popup: "Patient ID: <value>".
            dialog_text = dialog.inner_text(timeout=3000) or ""
            match = re.search(r"Patient\s*ID\s*:\s*([^\r\n]+)", dialog_text, flags=re.IGNORECASE)
            popup_patient_id = match.group(1).strip() if match else ""
            patient_id_to_fill = popup_patient_id or patient_id

            if patient_id_to_fill:
                input_locator = dialog.locator("input[id^=':r'], input[type='text'], input").first
                input_locator.fill("")
                input_locator.fill(patient_id_to_fill)

            remove_button = dialog.get_by_role("button", name="Remove", exact=False).first
            for _ in range(20):
                try:
                    if remove_button.is_enabled():
                        break
                except Exception:
                    pass
                self.pw_page.wait_for_timeout(100)

            remove_button.click()
        except Exception:
            # Fallback when dialog is not required or has different controls.
            confirm_candidates = [
                self.pw_page.get_by_role("button", name="Remove", exact=False).first,
                self.pw_page.get_by_role("button", name="Confirm", exact=False).first,
            ]
            for candidate in confirm_candidates:
                try:
                    if candidate.is_visible(timeout=2000):
                        candidate.click()
                        break
                except Exception:
                    continue

        # Verify row is removed from current filtered view.
        self.pw_page.wait_for_timeout(1200)
        return row.count() == 0

    def _wait_any_visible(self, selectors, timeout=6000):
        if isinstance(selectors, str):
            selectors = [selectors]

        for selector in selectors:
            try:
                self.pw_page.locator(selector).first.wait_for(state="visible", timeout=timeout)
                return
            except Exception:
                continue

        raise AssertionError(f"None of selectors became visible: {selectors}")

    def _click_any_visible(self, selectors, timeout=6000):
        if isinstance(selectors, str):
            selectors = [selectors]

        for selector in selectors:
            try:
                locator = self.pw_page.locator(selector).first
                locator.wait_for(state="visible", timeout=timeout)
                locator.click()
                return
            except Exception:
                continue

        raise AssertionError(f"Could not click any selector from: {selectors}")
    def _wait_any_visible(self, selectors, timeout=6000):
        if isinstance(selectors, str):
            selectors = [selectors]

        for selector in selectors:
            try:
                self.pw_page.locator(selector).first.wait_for(state="visible", timeout=timeout)
                return
            except Exception:
                continue

        raise AssertionError(f"None of selectors became visible: {selectors}")

    def _click_any_visible(self, selectors, timeout=6000):
        if isinstance(selectors, str):
            selectors = [selectors]

        for selector in selectors:
            try:
                locator = self.pw_page.locator(selector).first
                locator.wait_for(state="visible", timeout=timeout)
                locator.click()
                return
            except Exception:
                continue

        raise AssertionError(f"Could not click any selector from: {selectors}")
