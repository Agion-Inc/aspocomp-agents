/* Main application logic */

// Application state
const appState = {
    conversationId: null,
    currentModel: 'gemini-2.5-flash',
    mcpEnabled: false,
    messages: []
};

// DOM elements
const elements = {
    messagesContainer: null,
    messageInput: null,
    sendButton: null,
    modelSelector: null,
    clearButton: null,
    settingsButton: null,
    settingsModal: null,
    closeSettings: null,
    emptyMessage: null
};

/**
 * Initialize the application
 */
async function init() {
    // Get DOM elements
    elements.messagesContainer = document.getElementById('messages-container');
    elements.messageInput = document.getElementById('message-input');
    elements.sendButton = document.getElementById('send-btn');
    elements.modelSelector = document.getElementById('model-selector');
    elements.clearButton = document.getElementById('clear-btn');
    elements.settingsButton = document.getElementById('settings-btn');
    elements.settingsModal = document.getElementById('settings-modal');
    elements.closeSettings = document.getElementById('close-settings');
    elements.emptyMessage = document.getElementById('empty-message');
    
    // Handle splash screen
    const splashScreen = document.getElementById('splash-screen');
    const splashVideo = document.getElementById('splash-video');
    
    if (splashVideo) {
        splashVideo.onloadeddata = () => {
            // Video loaded, play it
            splashVideo.play().catch(err => {
                console.log('Autoplay prevented:', err);
            });
        };
        
        // Hide splash screen after video plays or after 3 seconds
        setTimeout(() => {
            if (splashScreen) {
                splashScreen.classList.add('hidden');
                setTimeout(() => {
                    splashScreen.remove();
                }, 500);
            }
        }, 3000);
    } else {
        // No splash video, remove splash screen immediately
        if (splashScreen) {
            splashScreen.remove();
        }
    }
    
    // Check API health
    try {
        await api.healthCheck();
        console.log('API is healthy');
    } catch (error) {
        showError('Cannot connect to API. Make sure the backend server is running.', elements.messagesContainer);
        console.error('API health check failed:', error);
    }
    
    // Load models
    try {
        const models = await api.getModels();
        // Models are already loaded in HTML
        console.log('Models loaded:', models);
    } catch (error) {
        console.error('Failed to load models:', error);
    }
    
    // Setup event listeners
    setupEventListeners();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Send button click
    elements.sendButton.addEventListener('click', handleSend);
    
    // Enter key to send (Shift+Enter for new line)
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // Auto-resize textarea
    elements.messageInput.addEventListener('input', () => {
        autoResizeTextarea(elements.messageInput);
        updateSendButton();
    });
    
    // Clear conversation
    elements.clearButton.addEventListener('click', handleClear);
    
    // Settings modal
    elements.settingsButton.addEventListener('click', () => {
        elements.settingsModal.setAttribute('aria-hidden', 'false');
    });
    
    elements.closeSettings.addEventListener('click', () => {
        elements.settingsModal.setAttribute('aria-hidden', 'true');
    });
    
    // Model selector change
    elements.modelSelector.addEventListener('change', (e) => {
        appState.currentModel = e.target.value;
    });
    
    // MCP toggle
    const mcpCheckbox = document.getElementById('mcp-enabled');
    mcpCheckbox.addEventListener('change', (e) => {
        appState.mcpEnabled = e.target.checked;
    });
}

/**
 * Handle send message with improved error handling
 */
async function handleSend() {
    const messageText = elements.messageInput.value.trim();
    
    if (!messageText) {
        return;
    }
    
    // Clear input
    elements.messageInput.value = '';
    autoResizeTextarea(elements.messageInput);
    updateSendButton();
    
    // Hide empty message
    if (elements.emptyMessage) {
        elements.emptyMessage.classList.add('hidden');
    }
    
    // Add user message to UI
    const userMessage = {
        id: generateId(),
        role: 'user',
        content: messageText,
        timestamp: new Date().toISOString()
    };
    
    renderMessage(userMessage, elements.messagesContainer);
    appState.messages.push(userMessage);
    
    // Show loading indicator
    showLoading(elements.messagesContainer);
    
    // Disable send button
    elements.sendButton.disabled = true;
    
    try {
        // Send to API
        const response = await api.sendMessage(messageText, {
            model: appState.currentModel,
            mcp_enabled: appState.mcpEnabled,
            conversation_id: appState.conversationId
        });
        
        // Update conversation ID
        if (response.conversation_id) {
            appState.conversationId = response.conversation_id;
        }
        
        // Remove loading indicator
        removeLoading();
        
        // Add assistant message to UI
        const assistantMessage = {
            id: generateId(),
            role: 'assistant',
            content: response.response,
            timestamp: response.timestamp || new Date().toISOString(),
            function_calls: response.function_calls || []
        };
        
        renderMessage(assistantMessage, elements.messagesContainer);
        appState.messages.push(assistantMessage);
        
    } catch (error) {
        removeLoading();
        
        // Enhanced error handling
        let errorMessage = 'An error occurred';
        
        if (error.message) {
            errorMessage = error.message;
        } else if (error instanceof TypeError && error.message.includes('fetch')) {
            errorMessage = 'Cannot connect to server. Make sure the backend is running on port 5001.';
        } else if (error.response) {
            // Handle HTTP error responses
            errorMessage = error.response.error || errorMessage;
        }
        
        // If conversation not found, clear it and retry
        if (errorMessage.includes('Conversation') && errorMessage.includes('not found')) {
            appState.conversationId = null;
            // Optionally retry automatically
            // await handleSend();
        }
        
        showError(`Error: ${errorMessage}`, elements.messagesContainer);
        console.error('Send message error:', error);
    } finally {
        // Re-enable send button
        elements.sendButton.disabled = false;
    }
}

/**
 * Handle clear conversation
 */
async function handleClear() {
    if (!appState.conversationId) {
        // Just clear UI
        clearMessages();
        return;
    }
    
    if (!confirm('Are you sure you want to clear this conversation?')) {
        return;
    }
    
    try {
        await api.clearConversation(appState.conversationId);
        appState.conversationId = null;
        clearMessages();
    } catch (error) {
        showError(`Error clearing conversation: ${error.message}`, elements.messagesContainer);
        console.error('Clear conversation error:', error);
    }
}

/**
 * Clear all messages from UI
 */
function clearMessages() {
    const messages = elements.messagesContainer.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());
    
    if (elements.emptyMessage) {
        elements.emptyMessage.classList.remove('hidden');
    }
    
    appState.messages = [];
}

/**
 * Update send button state
 */
function updateSendButton() {
    const hasText = elements.messageInput.value.trim().length > 0;
    elements.sendButton.disabled = !hasText;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

