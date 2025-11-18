"""Pytest configuration for E2E tests."""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


@pytest.fixture(scope="session")
def browser():
    """Create a browser instance for testing."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser):
    """Create a new page for testing."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

