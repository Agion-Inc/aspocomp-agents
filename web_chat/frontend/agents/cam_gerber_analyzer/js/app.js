/* Main application logic for CAM Gerber Analyzer */

// Application state
const appState = {
    conversationId: null,
    messages: [],
    selectedFiles: [],
    analysisId: null
};

// DOM elements
const elements = {
    uploadSection: null,
    uploadArea: null,
    fileInput: null,
    selectFilesBtn: null,
    fileList: null,
    fileListItems: null,
    analyzeBtn: null,
    clearFilesBtn: null,
    chatSection: null,
    messagesContainer: null,
    messageInput: null,
    sendButton: null,
    emptyMessage: null,
    analysisResults: null,
    analysisContent: null
};

/**
 * Initialize the application
 */
async function init() {
    // Get DOM elements
    elements.uploadSection = document.getElementById('upload-section');
    elements.uploadArea = document.getElementById('upload-area');
    elements.fileInput = document.getElementById('file-input');
    elements.selectFilesBtn = document.getElementById('select-files-btn');
    elements.fileList = document.getElementById('file-list');
    elements.fileListItems = document.getElementById('file-list-items');
    elements.analyzeBtn = document.getElementById('analyze-btn');
    elements.clearFilesBtn = document.getElementById('clear-files-btn');
    elements.chatSection = document.getElementById('chat-section');
    elements.messagesContainer = document.getElementById('messages-container');
    elements.messageInput = document.getElementById('message-input');
    elements.sendButton = document.getElementById('send-btn');
    elements.emptyMessage = document.getElementById('empty-message');
    elements.analysisResults = document.getElementById('analysis-results');
    elements.analysisContent = document.getElementById('analysis-content');
    
    // Event listeners
    elements.selectFilesBtn.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.analyzeBtn.addEventListener('click', handleAnalyze);
    elements.clearFilesBtn.addEventListener('click', handleClearFiles);
    elements.sendButton.addEventListener('click', handleSend);
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // Drag and drop
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);
    
    // Auto-resize textarea
    elements.messageInput.addEventListener('input', () => {
        elements.messageInput.style.height = 'auto';
        elements.messageInput.style.height = elements.messageInput.scrollHeight + 'px';
    });
}

/**
 * Handle file selection
 */
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

/**
 * Handle drag over
 */
function handleDragOver(e) {
    e.preventDefault();
    elements.uploadArea.classList.add('drag-over');
}

/**
 * Handle drag leave
 */
function handleDragLeave(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
}

/**
 * Handle drop
 */
function handleDrop(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

/**
 * Add files to selection
 */
function addFiles(files) {
    // Filter valid file types
    const validExtensions = ['.gbr', '.ger', '.art', '.drill', '.txt', '.tgz', '.zip', '.tar.gz', '.odb'];
    const validFiles = files.filter(file => {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        return validExtensions.some(validExt => file.name.toLowerCase().endsWith(validExt));
    });
    
    if (validFiles.length === 0) {
        alert('Valitse kelvolliset tiedostot (.gbr, .ger, .art, .drill, .txt, .tgz, .zip, .tar.gz, .odb)');
        return;
    }
    
    appState.selectedFiles = [...appState.selectedFiles, ...validFiles];
    updateFileList();
}

/**
 * Update file list display
 */
function updateFileList() {
    if (appState.selectedFiles.length === 0) {
        elements.fileList.style.display = 'none';
        return;
    }
    
    elements.fileList.style.display = 'block';
    elements.fileListItems.innerHTML = '';
    
    appState.selectedFiles.forEach((file, index) => {
        const li = document.createElement('li');
        li.className = 'file-list-item';
        
        const name = document.createElement('span');
        name.className = 'file-list-item__name';
        name.textContent = file.name;
        
        const size = document.createElement('span');
        size.className = 'file-list-item__size';
        size.textContent = formatFileSize(file.size);
        
        const remove = document.createElement('button');
        remove.className = 'file-list-item__remove';
        remove.textContent = '×';
        remove.addEventListener('click', () => {
            appState.selectedFiles.splice(index, 1);
            updateFileList();
        });
        
        li.appendChild(name);
        li.appendChild(size);
        li.appendChild(remove);
        elements.fileListItems.appendChild(li);
    });
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Handle clear files
 */
function handleClearFiles() {
    appState.selectedFiles = [];
    elements.fileInput.value = '';
    updateFileList();
}

/**
 * Handle analyze button click
 */
async function handleAnalyze() {
    if (appState.selectedFiles.length === 0) {
        alert('Valitse ensin tiedostot');
        return;
    }
    
    // Disable buttons
    elements.analyzeBtn.disabled = true;
    elements.clearFilesBtn.disabled = true;
    
    // Show chat section
    elements.uploadSection.style.display = 'none';
    elements.chatSection.style.display = 'flex';
    
    // Hide empty message
    if (elements.emptyMessage) {
        elements.emptyMessage.style.display = 'none';
    }
    
    // Show loading message
    addMessage('assistant', 'Lataan tiedostot ja aloitan analyysin...', true);
    
    try {
        // Convert files to base64
        const fileData = await Promise.all(
            appState.selectedFiles.map(async (file) => {
                const base64 = await fileToBase64(file);
                return {
                    filename: file.name,
                    content: base64,
                    file_type: detectFileType(file.name)
                };
            })
        );
        
        // Send message with files
        const message = `Analysoi nämä piirilevyn tiedostot ja luo kattava yhteenveto suunnittelusta.`;
        const response = await sendMessageWithFiles(message, appState.conversationId, fileData);
        
        // Remove loading message
        removeLastMessage();
        
        // Update conversation ID
        if (response.conversation_id) {
            appState.conversationId = response.conversation_id;
        }
        
        // Store analysis ID
        if (response.metadata && response.metadata.analysis_id) {
            appState.analysisId = response.metadata.analysis_id;
        }
        
        // Add assistant response
        if (response.response) {
            addMessage('assistant', response.response);
        }
        
        // Show analysis results if available
        if (response.metadata && response.metadata.summary) {
            showAnalysisResults(response.metadata.summary);
        }
        
    } catch (error) {
        removeLastMessage();
        addMessage('assistant', `Virhe: ${error.message}`);
    } finally {
        elements.analyzeBtn.disabled = false;
        elements.clearFilesBtn.disabled = false;
    }
}

/**
 * Detect file type from filename
 */
function detectFileType(filename) {
    const name = filename.toLowerCase();
    if (name.includes('top') && name.includes('copper')) return 'copper_top';
    if (name.includes('bottom') && name.includes('copper')) return 'copper_bottom';
    if (name.includes('solder') && name.includes('top')) return 'solder_mask_top';
    if (name.includes('solder') && name.includes('bottom')) return 'solder_mask_bottom';
    if (name.includes('silkscreen')) return 'silkscreen';
    if (name.includes('drill')) return 'drill';
    if (name.endsWith('.tgz') || name.endsWith('.zip') || name.endsWith('.tar.gz') || name.endsWith('.odb')) {
        return 'odbp_archive';
    }
    return 'other';
}

/**
 * Handle send button click
 */
async function handleSend() {
    const message = elements.messageInput.value.trim();
    if (!message) return;
    
    // Clear input
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';
    
    // Disable input
    elements.messageInput.disabled = true;
    elements.sendButton.disabled = true;
    
    // Add user message to UI
    addMessage('user', message);
    
    // Show loading indicator
    const loadingId = addMessage('assistant', '', true);
    
    try {
        // Send message to agent
        const response = await sendMessage(message, appState.conversationId);
        
        // Remove loading indicator
        removeMessage(loadingId);
        
        // Check if response indicates an error
        if (!response.success) {
            const errorMessage = response.error || 'Tuntematon virhe';
            addMessage('assistant', `Virhe: ${errorMessage}`);
            return;
        }
        
        // Update conversation ID
        if (response.conversation_id) {
            appState.conversationId = response.conversation_id;
        }
        
        // Add assistant response
        const responseText = response.response || response.text || '';
        if (responseText) {
            addMessage('assistant', responseText);
        } else {
            addMessage('assistant', 'Vastaus on tyhjä. Yritä uudelleen.');
        }
        
        // Update analysis results if available
        if (response.metadata && response.metadata.summary) {
            showAnalysisResults(response.metadata.summary);
        }
        
    } catch (error) {
        // Remove loading indicator
        removeMessage(loadingId);
        
        // Show error message
        addMessage('assistant', `Virhe: ${error.message}`);
    } finally {
        // Re-enable input
        elements.messageInput.disabled = false;
        elements.sendButton.disabled = false;
        elements.messageInput.focus();
    }
}

/**
 * Add a message to the chat
 */
function addMessage(role, text, loading = false) {
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message message--${role}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message__bubble';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message__text';
    
    if (loading) {
        textDiv.innerHTML = '<span class="loading"></span>';
    } else {
        // Simple text rendering (can be enhanced with markdown)
        textDiv.textContent = text;
    }
    
    bubble.appendChild(textDiv);
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message__timestamp';
    timestamp.textContent = new Date().toLocaleTimeString('fi-FI', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    bubble.appendChild(timestamp);
    
    messageDiv.appendChild(bubble);
    elements.messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
    
    return messageId;
}

/**
 * Remove a message from the chat
 */
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

/**
 * Remove last message
 */
function removeLastMessage() {
    const messages = elements.messagesContainer.querySelectorAll('.message');
    if (messages.length > 0) {
        messages[messages.length - 1].remove();
    }
}

/**
 * Show analysis results
 */
function showAnalysisResults(summary) {
    if (!summary) return;
    
    elements.analysisResults.style.display = 'block';
    
    let html = '<div class="analysis-summary">';
    
    // Basic info
    if (summary.file_count || summary.file_format) {
        html += '<div class="analysis-summary__section">';
        html += '<div class="analysis-summary__title">Tiedostot</div>';
        if (summary.file_format) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Muoto:</span><span class="analysis-summary__value">${summary.file_format.toUpperCase()}</span></div>`;
        }
        if (summary.file_count) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Tiedostoja:</span><span class="analysis-summary__value">${summary.file_count}</span></div>`;
        }
        if (summary.total_size_mb) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Koko:</span><span class="analysis-summary__value">${summary.total_size_mb} MB</span></div>`;
        }
        html += '</div>';
    }
    
    // Board dimensions
    if (summary.board_width || summary.board_height) {
        html += '<div class="analysis-summary__section">';
        html += '<div class="analysis-summary__title">Piirilevyn mitat</div>';
        if (summary.board_width && summary.board_height) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Koko:</span><span class="analysis-summary__value">${summary.board_width}mm × ${summary.board_height}mm</span></div>`;
        }
        if (summary.board_thickness) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Paksuus:</span><span class="analysis-summary__value">${summary.board_thickness}mm</span></div>`;
        }
        html += '</div>';
    }
    
    // Panel info
    if (summary.panel_count || summary.total_boards) {
        html += '<div class="analysis-summary__section">';
        html += '<div class="analysis-summary__title">Panelointi</div>';
        if (summary.panel_count) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Paneleita:</span><span class="analysis-summary__value">${summary.panel_count}</span></div>`;
        }
        if (summary.total_boards) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Piirilevyjä:</span><span class="analysis-summary__value">${summary.total_boards}</span></div>`;
        }
        html += '</div>';
    }
    
    // Layer info
    if (summary.layer_count) {
        html += '<div class="analysis-summary__section">';
        html += '<div class="analysis-summary__title">Kerrokset</div>';
        html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Kerroksia:</span><span class="analysis-summary__value">${summary.layer_count}</span></div>`;
        if (summary.inner_layer_count) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Sisäkerroksia:</span><span class="analysis-summary__value">${summary.inner_layer_count}</span></div>`;
        }
        html += '</div>';
    }
    
    // Materials
    if (summary.laminate_type || summary.surface_finish) {
        html += '<div class="analysis-summary__section">';
        html += '<div class="analysis-summary__title">Materiaalit</div>';
        if (summary.laminate_type) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Laminaatti:</span><span class="analysis-summary__value">${summary.laminate_type}</span></div>`;
        }
        if (summary.surface_finish) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Pintakäsittely:</span><span class="analysis-summary__value">${summary.surface_finish}</span></div>`;
        }
        html += '</div>';
    }
    
    // Design characteristics
    if (summary.total_vias || summary.total_pads) {
        html += '<div class="analysis-summary__section">';
        html += '<div class="analysis-summary__title">Suunnittelun ominaisuudet</div>';
        if (summary.total_vias) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Via-reikiä:</span><span class="analysis-summary__value">${summary.total_vias}</span></div>`;
        }
        if (summary.total_pads) {
            html += `<div class="analysis-summary__item"><span class="analysis-summary__label">Padeja:</span><span class="analysis-summary__value">${summary.total_pads}</span></div>`;
        }
        html += '</div>';
    }
    
    html += '</div>';
    
    elements.analysisContent.innerHTML = html;
    
    // Scroll to results
    elements.analysisResults.scrollIntoView({ behavior: 'smooth' });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

