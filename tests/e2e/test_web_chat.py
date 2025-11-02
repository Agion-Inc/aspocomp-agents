"""E2E tests using Playwright for web chat UI."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def page(browser):
    """Create a new page for testing."""
    page = browser.new_page()
    page.goto("http://localhost:5001")
    yield page
    page.close()


def test_page_loads(page: Page):
    """Test that the page loads successfully."""
    expect(page).to_have_title("Gemini Agent Chat")


def test_header_elements_exist(page: Page):
    """Test that header elements are present."""
    expect(page.get_by_role("heading", name="Gemini Agent Chat")).to_be_visible()
    expect(page.get_by_role("combobox")).to_be_visible()
    expect(page.get_by_role("button", name="Settings")).to_be_visible()
    expect(page.get_by_role("button", name="Clear conversation")).to_be_visible()


def test_message_input_exists(page: Page):
    """Test that message input exists."""
    expect(page.get_by_role("textbox", name="Message input")).to_be_visible()
    expect(page.get_by_role("button", name="Send message")).to_be_visible()


def test_send_button_disabled_when_empty(page: Page):
    """Test that send button is disabled when input is empty."""
    send_button = page.get_by_role("button", name="Send message")
    expect(send_button).to_be_disabled()


def test_send_button_enabled_when_text_entered(page: Page):
    """Test that send button is enabled when text is entered."""
    input_field = page.get_by_role("textbox", name="Message input")
    send_button = page.get_by_role("button", name="Send message")
    
    input_field.fill("Test message")
    expect(send_button).to_be_enabled()


def test_send_message_displays_user_message(page: Page):
    """Test that sending a message displays it in the chat."""
    input_field = page.get_by_role("textbox", name="Message input")
    send_button = page.get_by_role("button", name="Send message")
    
    input_field.fill("Hello, test")
    send_button.click()
    
    # Wait for user message to appear
    expect(page.get_by_text("Hello, test")).to_be_visible(timeout=10000)


def test_settings_modal_opens(page: Page):
    """Test that settings modal opens when clicked."""
    settings_button = page.get_by_role("button", name="Settings")
    settings_button.click()
    
    expect(page.get_by_role("heading", name="Settings")).to_be_visible()


def test_clear_conversation_shows_confirmation(page: Page):
    """Test that clear conversation shows confirmation dialog."""
    # First send a message to create conversation
    input_field = page.get_by_role("textbox", name="Message input")
    send_button = page.get_by_role("button", name="Send message")
    input_field.fill("Test")
    send_button.click()
    
    # Wait a bit for message to be sent
    page.wait_for_timeout(2000)
    
    # Click clear button
    clear_button = page.get_by_role("button", name="Clear conversation")
    
    # Set up dialog handler
    dialog_handled = False
    
    def handle_dialog(dialog):
        nonlocal dialog_handled
        dialog_handled = True
        dialog.accept()
    
    page.on("dialog", handle_dialog)
    clear_button.click()
    
    # Verify dialog was shown
    assert dialog_handled


def test_model_selector_works(page: Page):
    """Test that model selector dropdown works."""
    model_selector = page.get_by_role("combobox")
    expect(model_selector).to_be_visible()
    
    # Check default value
    expect(model_selector).to_have_value("gemini-2.5-flash")
    
    # Change model
    model_selector.select_option("gemini-2.5-pro")
    expect(model_selector).to_have_value("gemini-2.5-pro")

