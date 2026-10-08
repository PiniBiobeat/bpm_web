import logging

import pytest
from dotenv import load_dotenv

from infra.browser_online import BrowserOnline
from infra.config.config_provider import configuration, init_config
from infra.teardown.tear_down import tear_down_tasks
from logic.pages.login_page import LogInOnline


load_dotenv()

logging.getLogger().setLevel(logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption("--config", action="store", default="config.ini")


def pytest_configure(config):
    init_config(config.getoption('--config'))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose each phase's report on the item (item.rep_setup / rep_call / rep_teardown)."""
    outcome = yield
    setattr(item, "rep_" + call.when, outcome.get_result())


def _run_tear_down_tasks():
    print('\r******TEARDOWN******')
    for tear_down in tear_down_tasks:
        try:
            tear_down.invoke()
        except Exception:
            pass
    tear_down_tasks.clear()
    print('\r*****DONE_TEARDOWN*****')


@pytest.fixture
def browser_online(request):
    """A fresh browser per test; saves a trace on failure and always cleans up."""
    print(f'Starting test "{request.node.originalname}"')
    browser = BrowserOnline()
    yield browser

    call_report = getattr(request.node, "rep_call", None)
    if call_report is not None and call_report.failed:
        try:
            browser.stop_trace()
        except Exception:
            pass
    _run_tear_down_tasks()
    browser.close()
    print('\r*****DONE*****')


@pytest.fixture
def login_page(browser_online) -> LogInOnline:
    """The login page of the staging environment, already opened."""
    return browser_online.navigate(configuration["online_url_stage"], LogInOnline)
