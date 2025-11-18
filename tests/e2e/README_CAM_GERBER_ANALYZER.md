# CAM Gerber Analyzer UI E2E Tests

Playwright E2E tests for the CAM Gerber Analyzer UI.

## Prerequisites

1. **Install Playwright and pytest-playwright:**
   ```bash
   pip3 install pytest-playwright playwright
   playwright install chromium
   ```

2. **Start the Flask server:**
   ```bash
   cd web_chat/backend
   python3 app.py
   ```
   The server should be running on `http://localhost:5000`

## Running Tests

### Run all CAM Gerber Analyzer UI tests:
```bash
pytest tests/e2e/test_cam_gerber_analyzer_ui.py -v --base-url=http://localhost:5000
```

### Run specific test:
```bash
pytest tests/e2e/test_cam_gerber_analyzer_ui.py::test_cam_gerber_analyzer_page_loads -v --base-url=http://localhost:5000
```

### Run with browser visible (headed mode):
```bash
pytest tests/e2e/test_cam_gerber_analyzer_ui.py -v --base-url=http://localhost:5000 --headed
```

## Test Coverage

The test suite covers:

1. **Page Loading**
   - `test_cam_gerber_analyzer_page_loads` - Verifies page loads and displays correctly

2. **File Upload UI**
   - `test_file_upload_area_visible` - Checks upload area is visible
   - `test_file_selection_button_click` - Tests file selection button
   - `test_file_upload_with_zip` - Tests uploading ZIP files
   - `test_file_list_display` - Verifies file list shows correctly
   - `test_remove_file_from_list` - Tests removing files from list
   - `test_clear_files_button` - Tests clear files functionality

3. **UI State**
   - `test_chat_section_hidden_initially` - Verifies chat is hidden initially
   - `test_analysis_results_hidden_initially` - Verifies results are hidden initially
   - `test_message_input_exists` - Checks message input exists

4. **Navigation**
   - `test_back_link_navigation` - Tests back link works

5. **Responsive Design**
   - `test_ui_responsive_layout` - Tests responsive layout

6. **Validation**
   - `test_analyze_button_disabled_without_files` - Tests validation logic

## Test File Requirements

For file upload tests to work, ensure `data/cam_gerber_analyzer/uploads/PCB.zip` exists, or tests will be skipped.

## Environment Variables

- `BASE_URL` - Override base URL (default: `http://localhost:5000`)

## Notes

- Tests will skip if the Flask server is not running
- Tests will skip if required test files are not found
- Tests use headless browser by default (use `--headed` to see browser)

