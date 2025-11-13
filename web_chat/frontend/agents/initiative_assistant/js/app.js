/* Main application logic for Initiative Assistant */

// Application state
const appState = {
    conversationId: null,
    messages: []
};

// DOM elements
const elements = {
    messagesContainer: null,
    messageInput: null,
    sendButton: null,
    emptyMessage: null,
    similarInitiatives: null,
    similarList: null
};

/**
 * Initialize the application
 */
async function init() {
    // Get DOM elements
    elements.messagesContainer = document.getElementById('messages-container');
    elements.messageInput = document.getElementById('message-input');
    elements.sendButton = document.getElementById('send-btn');
    elements.emptyMessage = document.getElementById('empty-message');
    elements.similarInitiatives = document.getElementById('similar-initiatives');
    elements.similarList = document.getElementById('similar-list');
    
    // Event listeners
    elements.sendButton.addEventListener('click', handleSend);
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // Auto-resize textarea
    elements.messageInput.addEventListener('input', () => {
        elements.messageInput.style.height = 'auto';
        elements.messageInput.style.height = elements.messageInput.scrollHeight + 'px';
    });
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
    
    // Hide empty message
    if (elements.emptyMessage) {
        elements.emptyMessage.style.display = 'none';
    }
    
    // Add user message to UI
    addMessage('user', message);
    
    // Show loading indicator
    const loadingId = addMessage('assistant', '', true);
    
    try {
        // Send message to agent
        const response = await sendMessage(message, appState.conversationId);
        
        // Update conversation ID
        if (response.conversation_id) {
            appState.conversationId = response.conversation_id;
        }
        
        // Remove loading indicator
        removeMessage(loadingId);
        
        // Add assistant response
        addMessage('assistant', response.response);
        
        // Show similar initiatives if found
        if (response.metadata && response.metadata.similar_initiatives_found) {
            showSimilarInitiatives(response.metadata.similar_initiatives_found);
        }
        
        // Handle function calls
        if (response.function_calls && response.function_calls.length > 0) {
            // Function calls are handled by the agent, but we can show indicators
            console.log('Function calls:', response.function_calls);
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
 * @param {string} role - 'user' or 'assistant'
 * @param {string} text - Message text
 * @param {boolean} loading - Show loading indicator
 * @returns {string} Message ID
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
 * @param {string} messageId - Message ID to remove
 */
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

/**
 * Show similar initiatives
 * @param {Array} initiatives - List of similar initiatives
 */
function showSimilarInitiatives(initiatives) {
    if (!initiatives || initiatives.length === 0) {
        elements.similarInitiatives.style.display = 'none';
        return;
    }
    
    elements.similarList.innerHTML = '';
    
    initiatives.forEach(initiative => {
        const item = document.createElement('div');
        item.className = 'similar-item';
        
        const title = document.createElement('div');
        title.className = 'similar-item__title';
        title.textContent = initiative.title || 'Nimetön aloite';
        item.appendChild(title);
        
        if (initiative.description) {
            const desc = document.createElement('div');
            desc.className = 'similar-item__description';
            desc.textContent = initiative.description.substring(0, 150) + (initiative.description.length > 150 ? '...' : '');
            item.appendChild(desc);
        }
        
        const meta = document.createElement('div');
        meta.className = 'similar-item__meta';
        const status = initiative.status || 'proposed';
        const date = initiative.created_at ? new Date(initiative.created_at).toLocaleDateString('fi-FI') : '';
        meta.textContent = `Status: ${status}${date ? ` | Luotu: ${date}` : ''}`;
        item.appendChild(meta);
        
        elements.similarList.appendChild(item);
    });
    
    elements.similarInitiatives.style.display = 'block';
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

