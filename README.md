# BPM Web Automation

UI test automation project for BPM web flows using Playwright + pytest with a page-object structure.

## What this project covers

- Login flows (sanity, error handling, expired password scenarios)
- Administrator role flows (metric/imperial sanity, boundary values, error handling)
- Session management and patient admission behaviors

## Tech stack

- Python
- pytest
- Playwright (sync API)
- pytest-html
- Allure (allure-pytest)

## Project layout

- `infra/` - browser wrappers, base page, config loader, helpers, teardown hooks
- `logic/pages/` - page objects used by tests
- `tests/` - test suites by feature area
- `config.ini` - runtime target URLs and global settings
- `.env` - credential and test data variables (local only)

## Prerequisites

- Python 3.9+
- Pip
- Chromium dependencies installed by Playwright

## Local setup

1. Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Install Playwright browser(s).

```powershell
python -m playwright install chromium
```

4. Create local environment variables.

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set real values.

## Configuration

- Default pytest config file option:
  - `--config config.ini`
- If not provided, the framework uses `config.ini` by default.
- Primary URLs are under `[GLOBAL]` in `config.ini`, including:
  - `online_url`
  - `online_url_stage`

## Environment variables

Common variables used by tests:

- `ADMIN_METRIC_EMAIL`
- `ADMIN_METRIC_PASSWORD`
- `EXPIRED_USER_EMAIL`
- `EXPIRED_USER_PASSWORD`
- `EXPIRED_USER_VERIFICATION_CODE`
- `EXPIRED_USER_USED_PASSWORD`
- `ADMIN_IMPERIAL_EMAIL`
- `ADMIN_IMPERIAL_PASSWORD`
- `USED_DEVICE_ID`
- `USED_DEVICE_ID_ERROR`
- `INACTIVE_DEVICE_ID`
- `INACTIVE_DEVICE_ID_ERROR`

Notes:

- Some tests skip automatically when required credentials are missing.
- Login page object blocks `None` credentials and raises a clear error.

## Running tests

Run full suite:

```powershell
pytest -vv
```

Run smoke tests:

```powershell
pytest -m smoke -vv
```

Run login suite only:

```powershell
pytest tests/login -vv
```

Run administrator role suite only:

```powershell
pytest tests/administrator_role -vv
```

Run with reports similar to CI:

```powershell
pytest -vv --tracing=retain-on-failure --alluredir=allure-results --junitxml=test-results/junit.xml --html=test-results/pytest-report.html --self-contained-html
```

## Artifacts and reporting

- Playwright trace file on test failure:
  - `test-results/trace.zip`
- Allure raw results:
  - `allure-results/`
- HTML report (when enabled):
  - `test-results/pytest-report.html`
- JUnit XML (when enabled):
  - `test-results/junit.xml`

## Headless behavior

`infra/browser_online.py` launches Chromium headless automatically when either of these is set:

- `CI=true`
- `GITHUB_ACTIONS=true`

Otherwise, local execution is headed by default.

## Docker execution

Build image:

```powershell
docker build -t bpm-web-auto .
```

Run tests in container:

```powershell
docker run --rm --env-file .env -v ${PWD}/allure-results:/app/allure-results -v ${PWD}/test-results:/app/test-results bpm-web-auto
```

## Utility script

`parse_jira_issue.py` reads `issueData.json` and prints a filter string from linked issue IDs.
