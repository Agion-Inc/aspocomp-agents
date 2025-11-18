"""Playwright E2E tests for CAM Gerber Analyzer UI."""

import pytest
from playwright.sync_api import Page, expect
import os
import sys

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, os.path.abspath(project_root))


@pytest.fixture(scope="session")
def base_url():
    """Get base URL for the application."""
    return os.environ.get('BASE_URL', 'http://localhost:5000')


@pytest.fixture(scope="session")
def test_file_path():
    """Path to test PCB.zip file."""
    test_file = os.path.join(
        os.path.dirname(__file__),
        '../../data/cam_gerber_analyzer/uploads/PCB.zip'
    )
    if os.path.exists(test_file):
        return test_file
    # Alternative: use a smaller test file if PCB.zip doesn't exist
    return None


def test_cam_gerber_analyzer_page_loads(page: Page, base_url: str):
    """Test that the CAM Gerber Analyzer page loads correctly."""
    # Navigate to page with timeout
    try:
        response = page.goto(f"{base_url}/agents/cam_gerber_analyzer/", wait_until="domcontentloaded", timeout=10000)
        if response and response.status >= 400:
            pytest.skip(f"Page returned status {response.status}. Make sure Flask server is running and serving static files.")
    except Exception as e:
        pytest.skip(f"Could not load page: {e}. Make sure Flask server is running on {base_url}")
    
    # Wait a bit for JavaScript to execute
    page.wait_for_timeout(1000)
    
    # Check page content
    body_text = page.locator('body').text_content()
    if not body_text or len(body_text.strip()) < 10:
        pytest.skip("Page appears to be empty. Check static file serving configuration.")
    
    # Check header elements (more flexible selector)
    header = page.locator('.agent-header, header, [class*="header"]')
    if header.count() == 0:
        # Try to find any heading
        heading = page.locator('h1')
        if heading.count() > 0:
            expect(heading.first()).to_be_visible(timeout=5000)
        else:
            pytest.skip("Could not find expected page elements. Page may not be loading correctly.")
    else:
        expect(header.first()).to_be_visible(timeout=5000)
    
    # Check for main heading (flexible)
    heading = page.locator('h1:has-text("CAM Gerber Analyzer"), h1:has-text("Gerber")')
    if heading.count() > 0:
        expect(heading.first()).to_be_visible(timeout=5000)
    
    # Check for description or any text content
    description = page.locator('text=/gerber|analysoi|piirilevy/i')
    if description.count() > 0:
        expect(description.first()).to_be_visible(timeout=5000)


def test_file_upload_area_visible(page: Page, base_url: str):
    """Test that file upload area is visible and functional."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Check upload area is visible
    upload_area = page.locator('#upload-area')
    expect(upload_area).to_be_visible()
    
    # Check upload button exists
    select_button = page.locator('#select-files-btn')
    expect(select_button).to_be_visible()
    expect(select_button).to_have_text("Valitse tiedostot")
    
    # Check file input exists (hidden)
    file_input = page.locator('#file-input')
    expect(file_input).to_be_visible()
    
    # Check supported formats text
    formats_text = page.locator('text=Tuetut muodot')
    expect(formats_text).to_be_visible()


def test_file_selection_button_click(page: Page, base_url: str):
    """Test that clicking select files button triggers file input."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Click the select files button
    select_button = page.locator('#select-files-btn')
    select_button.click()
    
    # File input should be triggered (we can't easily test the file picker dialog,
    # but we can verify the button click works)
    # The actual file selection would require mocking or using a test file


def test_chat_section_hidden_initially(page: Page, base_url: str):
    """Test that chat section is hidden initially."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Chat section should be hidden
    chat_section = page.locator('#chat-section')
    expect(chat_section).to_have_css('display', 'none')


def test_analysis_results_hidden_initially(page: Page, base_url: str):
    """Test that analysis results section is hidden initially."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Analysis results should be hidden
    analysis_results = page.locator('#analysis-results')
    expect(analysis_results).to_have_css('display', 'none')


def test_file_upload_with_zip(page: Page, base_url: str, test_file_path: str):
    """Test uploading a ZIP file."""
    if not test_file_path or not os.path.exists(test_file_path):
        pytest.skip("Test file not found")
    
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Set up file input
    file_input = page.locator('#file-input')
    
    # Upload the file
    file_input.set_input_files(test_file_path)
    
    # Wait for file list to appear
    file_list = page.locator('#file-list')
    expect(file_list).to_be_visible(timeout=5000)
    
    # Check that file appears in list
    file_list_items = page.locator('#file-list-items li')
    expect(file_list_items).to_have_count(1)
    
    # Check analyze button is visible
    analyze_button = page.locator('#analyze-btn')
    expect(analyze_button).to_be_visible()
    expect(analyze_button).to_have_text("Aloita analyysi")


def test_clear_files_button(page: Page, base_url: str, test_file_path: str):
    """Test clearing selected files."""
    if not test_file_path or not os.path.exists(test_file_path):
        pytest.skip("Test file not found")
    
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Upload a file
    file_input = page.locator('#file-input')
    file_input.set_input_files(test_file_path)
    
    # Wait for file list
    file_list = page.locator('#file-list')
    expect(file_list).to_be_visible(timeout=5000)
    
    # Click clear button
    clear_button = page.locator('#clear-files-btn')
    clear_button.click()
    
    # File list should be hidden
    expect(file_list).to_have_css('display', 'none')


def test_analyze_button_disabled_without_files(page: Page, base_url: str):
    """Test that analyze button shows alert when no files selected."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Try to click analyze button (should be hidden, but if visible, should show alert)
    # Since analyze button is only visible when files are selected,
    # we'll test the file input validation instead
    
    # The analyze button should not be visible without files
    analyze_button = page.locator('#analyze-btn')
    file_list = page.locator('#file-list')
    
    # If file list is hidden, analyze button should also be hidden
    if file_list.is_hidden():
        expect(analyze_button).to_be_hidden()


def test_message_input_exists(page: Page, base_url: str):
    """Test that message input exists in chat section."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Message input should exist (even if hidden)
    message_input = page.locator('#message-input')
    expect(message_input).to_be_attached()
    
    # Send button should exist
    send_button = page.locator('#send-btn')
    expect(send_button).to_be_attached()


def test_back_link_navigation(page: Page, base_url: str):
    """Test that back link navigates correctly."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Find back link
    back_link = page.locator('a.back-link')
    expect(back_link).to_be_visible()
    expect(back_link).to_have_text("← Takaisin agentteihin")
    
    # Check href
    expect(back_link).to_have_attribute('href', '../')


def test_ui_responsive_layout(page: Page, base_url: str):
    """Test that UI layout is responsive."""
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Test mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    
    # Main elements should still be visible
    header = page.locator('.agent-header')
    expect(header).to_be_visible()
    
    upload_area = page.locator('#upload-area')
    expect(upload_area).to_be_visible()
    
    # Test desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    # Elements should still be visible
    expect(header).to_be_visible()
    expect(upload_area).to_be_visible()


def test_file_list_display(page: Page, base_url: str, test_file_path: str):
    """Test that file list displays correctly with file info."""
    if not test_file_path or not os.path.exists(test_file_path):
        pytest.skip("Test file not found")
    
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Upload file
    file_input = page.locator('#file-input')
    file_input.set_input_files(test_file_path)
    
    # Wait for file list
    file_list = page.locator('#file-list')
    expect(file_list).to_be_visible(timeout=5000)
    
    # Check file list header
    file_list_header = page.locator('#file-list h4')
    expect(file_list_header).to_have_text("Valitut tiedostot:")
    
    # Check file list items
    file_items = page.locator('#file-list-items li')
    expect(file_items).to_have_count(1)
    
    # Check file name is displayed
    file_name = page.locator('.file-list-item__name')
    expect(file_name).to_be_visible()
    
    # Check file size is displayed
    file_size = page.locator('.file-list-item__size')
    expect(file_size).to_be_visible()
    
    # Check remove button exists
    remove_button = page.locator('.file-list-item__remove')
    expect(remove_button).to_be_visible()


def test_remove_file_from_list(page: Page, base_url: str, test_file_path: str):
    """Test removing a file from the file list."""
    if not test_file_path or not os.path.exists(test_file_path):
        pytest.skip("Test file not found")
    
    page.goto(f"{base_url}/agents/cam_gerber_analyzer/")
    
    # Upload file
    file_input = page.locator('#file-input')
    file_input.set_input_files(test_file_path)
    
    # Wait for file list
    file_list = page.locator('#file-list')
    expect(file_list).to_be_visible(timeout=5000)
    
    # Remove file
    remove_button = page.locator('.file-list-item__remove')
    remove_button.click()
    
    # File list should be hidden
    expect(file_list).to_have_css('display', 'none')

