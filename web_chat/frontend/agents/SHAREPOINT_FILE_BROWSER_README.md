# SharePoint File Browser Component

A reusable file browser component for browsing, uploading, and downloading files from SharePoint. This component can be easily integrated into any agent UI.

## Features

- 📁 Browse SharePoint files and folders
- ⬆️ Upload files to SharePoint
- ⬇️ Download files from SharePoint
- 🔄 Refresh file list
- 📱 Responsive design
- 🎨 Consistent styling with agent UI theme

## Integration

### Basic Integration

To add the SharePoint file browser to any agent UI, include the HTML component in your page:

```html
<!-- Include the SharePoint file browser component -->
<div id="sharepoint-browser-container"></div>

<script>
    // Load the component
    fetch('/agents/sharepoint-file-browser.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('sharepoint-browser-container').innerHTML = html;
        });
</script>
```

### Direct Include (Recommended)

For better performance, directly include the component files:

```html
<!-- In your agent's index.html -->
<link rel="stylesheet" href="/agents/sharepoint-file-browser.css">

<!-- Include the component HTML -->
<div id="sharepoint-browser-container">
    <!-- Copy content from sharepoint-file-browser.html -->
</div>

<script src="/agents/sharepoint-file-browser.js"></script>
```

## Usage

### Listening to File Selection Events

The component dispatches a custom event when a file is selected:

```javascript
document.addEventListener('sharepoint-file-selected', (event) => {
    const { fileId, filename, isFolder, folderPath } = event.detail;
    
    if (isFolder) {
        console.log('Folder selected:', filename);
        // Component automatically navigates into folders
    } else {
        console.log('File selected:', filename);
        console.log('File ID:', fileId);
        // Use the file ID for your agent's operations
    }
});
```

### Programmatic Control

You can control the component programmatically:

```javascript
// Load files in a specific folder
sharepointFileBrowser.setCurrentFolder('Documents/Projects');

// Refresh current folder
sharepointFileBrowser.loadFiles();

// Download a file
sharepointFileBrowser.downloadFile(fileId, filename);

// Get current folder path
const currentFolder = sharepointFileBrowser.getCurrentFolder();
```

## API Endpoints

The component uses the following backend API endpoints:

- `GET /api/sharepoint/files?folder=<path>` - List files in folder
- `POST /api/sharepoint/upload` - Upload file
- `GET /api/sharepoint/download/<file_id>` - Get download URL

All endpoints require authentication (Azure AD).

## Configuration

The component uses SharePoint configuration from environment variables:

- `GLOBAL_SHAREPOINT_SITE_ID` - SharePoint site ID
- `SHAREPOINT_FOLDER_PATH` - Default folder path (defaults to "General")

## Styling

The component uses CSS variables for theming. It automatically adapts to your agent UI's color scheme:

- `--color-bg-primary` - Background color
- `--color-border` - Border color
- `--color-black` - Text color
- `--color-gray-medium` - Secondary text color
- `--spacing-*` - Spacing variables

## Example Integration

### Initiative Assistant Example

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/agents/sharepoint-file-browser.css">
</head>
<body>
    <h1>Initiative Assistant</h1>
    
    <!-- Include SharePoint file browser -->
    <div id="sharepoint-browser-container">
        <!-- Component HTML here -->
    </div>
    
    <script src="/agents/sharepoint-file-browser.js"></script>
    <script>
        // Listen for file selection
        document.addEventListener('sharepoint-file-selected', (event) => {
            const { fileId, filename, isFolder } = event.detail;
            
            if (!isFolder) {
                // Use the selected file in your agent logic
                console.log('Selected file for initiative:', filename);
            }
        });
    </script>
</body>
</html>
```

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires ES6+ support
- Requires Fetch API support

## Notes

- The component requires Azure AD authentication
- File uploads are limited by SharePoint quotas
- Large files may take time to upload/download
- The component automatically handles authentication tokens from the session

