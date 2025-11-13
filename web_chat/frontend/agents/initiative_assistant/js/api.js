/* API client for Initiative Assistant Agent */

const AGENT_ID = 'initiative_assistant';
const API_BASE = '/api/chat';

/**
 * Send a message to the Initiative Assistant agent
 * @param {string} message - User message
 * @param {string} conversationId - Optional conversation ID
 * @returns {Promise<Object>} Response from agent
 */
async function sendMessage(message, conversationId = null) {
    const response = await fetch(`${API_BASE}/${AGENT_ID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            conversation_id: conversationId,
            context: {
                user_id: getUserId(),
                department: getDepartment()
            }
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to send message');
    }
    
    return await response.json();
}

/**
 * Get user ID from context (placeholder)
 * @returns {string} User ID
 */
function getUserId() {
    // TODO: Get from authentication context
    return 'user_' + Date.now();
}

/**
 * Get user department from context (placeholder)
 * @returns {string} Department
 */
function getDepartment() {
    // TODO: Get from authentication context
    return 'unknown';
}

