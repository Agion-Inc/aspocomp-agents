/* SharePoint File Browser Component JavaScript */

(function() {
    'use strict';
    
    // Component state
    let currentFolder = null;
    let selectedFiles = [];
    
    // Get session token for API calls
    function getSessionToken() {
        return document.cookie
            .split('; ')
            .find(row => row.startsWith('azure_session='))
            ?.split('=')[1] || null;
    }
    
    // API call helper
    async function apiCall(endpoint, options = {}) {
        const token = getSessionToken();
        const defaultOptions = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'X-Session-Token': token })
            }
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(endpoint, mergedOptions);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    // Format date
    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Get file icon SVG
    function getFileIcon(isFolder, mimeType) {
        if (isFolder) {
            return `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"></path>
            </svg>`;
        }
        
        // File icon
        return `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
        </svg>`;
    }
    
    // Load files from SharePoint
    async function loadFiles(folderPath = null) {
        const loadingEl = document.getElementById('files-loading');
        const errorEl = document.getElementById('files-error');
        const listEl = document.getElementById('files-list');
        
        loadingEl.style.display = 'block';
        errorEl.style.display = 'none';
        listEl.innerHTML = '';
        
        try {
            const params = folderPath ? `?folder=${encodeURIComponent(folderPath)}` : '';
            const data = await apiCall(`/api/sharepoint/files${params}`);
            
            loadingEl.style.display = 'none';
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load files');
            }
            
            const files = data.files || [];
            
            if (files.length === 0) {
                listEl.innerHTML = '<p style="text-align: center; color: var(--color-gray-medium, #666); padding: var(--spacing-xl, 32px);">No files found</p>';
                return;
            }
            
            // Sort: folders first, then files
            files.sort((a, b) => {
                if (a.isFolder && !b.isFolder) return -1;
                if (!a.isFolder && b.isFolder) return 1;
                return a.name.localeCompare(b.name);
            });
            
            listEl.innerHTML = files.map(file => `
                <div class="file-browser__item ${file.isFolder ? 'file-browser__item--folder' : ''}" data-file-id="${file.id}" data-is-folder="${file.isFolder}">
                    <div class="file-browser__item-icon">
                        ${getFileIcon(file.isFolder, file.mimeType)}
                    </div>
                    <div class="file-browser__item-info">
                        <div class="file-browser__item-name">${escapeHtml(file.name)}</div>
                        <div class="file-browser__item-meta">
                            ${file.size ? `<span>${formatFileSize(file.size)}</span>` : ''}
                            ${file.lastModifiedDateTime ? `<span>Modified: ${formatDate(file.lastModifiedDateTime)}</span>` : ''}
                            ${file.createdBy ? `<span>By: ${escapeHtml(file.createdBy)}</span>` : ''}
                        </div>
                    </div>
                    <div class="file-browser__item-actions">
                        ${!file.isFolder ? `
                            <button class="file-browser__action-btn" onclick="sharepointFileBrowser.downloadFile('${file.id}', '${escapeHtml(file.name)}')" aria-label="Download">
                                <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M17 8v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8M7 12l3 3 3-3M10 15V3"/>
                                </svg>
                            </button>
                        ` : ''}
                        <button class="file-browser__action-btn" onclick="sharepointFileBrowser.selectFile('${file.id}', '${escapeHtml(file.name)}', ${file.isFolder})" aria-label="Select">
                            <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            loadingEl.style.display = 'none';
            errorEl.style.display = 'block';
            document.getElementById('error-message').textContent = error.message || 'Failed to load files';
            console.error('Error loading files:', error);
        }
    }
    
    // Download file
    async function downloadFile(fileId, filename) {
        try {
            const data = await apiCall(`/api/sharepoint/download/${fileId}`);
            
            if (!data.success || !data.downloadUrl) {
                throw new Error(data.error || 'Failed to get download URL');
            }
            
            // Open download URL in new tab
            window.open(data.downloadUrl, '_blank');
        } catch (error) {
            alert('Failed to download file: ' + (error.message || 'Unknown error'));
            console.error('Error downloading file:', error);
        }
    }
    
    // Select file (trigger event for parent component)
    function selectFile(fileId, filename, isFolder) {
        const event = new CustomEvent('sharepoint-file-selected', {
            detail: {
                fileId: fileId,
                filename: filename,
                isFolder: isFolder,
                folderPath: currentFolder
            }
        });
        document.dispatchEvent(event);
        
        // If folder, navigate into it
        if (isFolder) {
            const newFolderPath = currentFolder ? `${currentFolder}/${filename}` : filename;
            currentFolder = newFolderPath;
            loadFiles(currentFolder);
        }
    }
    
    // Upload file
    async function uploadFile(file, folderPath = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (folderPath) {
            formData.append('folder', folderPath);
        }
        
        const token = getSessionToken();
        const headers = {};
        if (token) {
            headers['X-Session-Token'] = token;
        }
        
        try {
            const response = await fetch('/api/sharepoint/upload', {
                method: 'POST',
                credentials: 'include',
                headers: headers,
                body: formData
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Upload failed');
            }
            
            return data;
        } catch (error) {
            console.error('Error uploading file:', error);
            throw error;
        }
    }
    
    // Initialize upload modal
    function initUploadModal() {
        const modal = document.getElementById('upload-modal');
        const openBtn = document.getElementById('upload-file-btn');
        const closeBtn = document.getElementById('close-upload-modal');
        const cancelBtn = document.getElementById('cancel-upload-btn');
        const fileInput = document.getElementById('file-input');
        const selectBtn = document.getElementById('select-files-btn');
        const uploadForm = document.getElementById('upload-form');
        const selectedFilesEl = document.getElementById('selected-files');
        const selectedFilesList = document.getElementById('selected-files-list');
        const submitBtn = document.getElementById('submit-upload-btn');
        
        // Open modal
        openBtn.addEventListener('click', () => {
            modal.style.display = 'flex';
            selectedFiles = [];
            fileInput.value = '';
            selectedFilesEl.style.display = 'none';
            submitBtn.disabled = true;
        });
        
        // Close modal
        const closeModal = () => {
            modal.style.display = 'none';
            selectedFiles = [];
            fileInput.value = '';
            selectedFilesEl.style.display = 'none';
        };
        
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        // Select files button
        selectBtn.addEventListener('click', () => {
            fileInput.click();
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            selectedFiles = Array.from(e.target.files);
            updateSelectedFilesList();
        });
        
        // Drag and drop
        const dropzone = document.getElementById('upload-area');
        
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--color-black, #000)';
        });
        
        dropzone.addEventListener('dragleave', () => {
            dropzone.style.borderColor = 'var(--color-border, #e5e5e5)';
        });
        
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--color-border, #e5e5e5)';
            
            const files = Array.from(e.dataTransfer.files);
            selectedFiles = files;
            fileInput.files = e.dataTransfer.files;
            updateSelectedFilesList();
        });
        
        // Update selected files list
        function updateSelectedFilesList() {
            if (selectedFiles.length === 0) {
                selectedFilesEl.style.display = 'none';
                submitBtn.disabled = true;
                return;
            }
            
            selectedFilesEl.style.display = 'block';
            selectedFilesList.innerHTML = selectedFiles.map(file => 
                `<li>${escapeHtml(file.name)} (${formatFileSize(file.size)})</li>`
            ).join('');
            submitBtn.disabled = false;
        }
        
        // Submit upload
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (selectedFiles.length === 0) {
                return;
            }
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Uploading...';
            
            try {
                for (const file of selectedFiles) {
                    await uploadFile(file, currentFolder);
                }
                
                alert('Files uploaded successfully!');
                closeModal();
                loadFiles(currentFolder);
            } catch (error) {
                alert('Upload failed: ' + (error.message || 'Unknown error'));
                submitBtn.disabled = false;
                submitBtn.textContent = 'Upload';
            }
        });
    }
    
    // Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Initialize component
    function init() {
        // Load files on init
        loadFiles();
        
        // Refresh button
        document.getElementById('refresh-files-btn').addEventListener('click', () => {
            loadFiles(currentFolder);
        });
        
        // Initialize upload modal
        initUploadModal();
    }
    
    // Export public API
    window.sharepointFileBrowser = {
        loadFiles: loadFiles,
        downloadFile: downloadFile,
        selectFile: selectFile,
        uploadFile: uploadFile,
        getCurrentFolder: () => currentFolder,
        setCurrentFolder: (folder) => {
            currentFolder = folder;
            loadFiles(folder);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

