/* API client for CAM Gerber Analyzer Agent */

const AGENT_ID = 'cam_gerber_analyzer';
const API_BASE = '/api/chat';

/**
 * Send a message to the CAM Gerber Analyzer agent
 * @param {string} message - User message
 * @param {string} conversationId - Optional conversation ID
 * @param {Array} files - Optional array of files
 * @returns {Promise<Object>} Response from agent
 */
async function sendMessage(message, conversationId = null, files = []) {
    const formData = new FormData();
    formData.append('message', message);
    if (conversationId) {
        formData.append('conversation_id', conversationId);
    }
    
    // Add files if provided
    files.forEach((file, index) => {
        formData.append(`files[${index}]`, file);
    });
    
    const response = await fetch(`${API_BASE}/${AGENT_ID}`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to send message');
    }
    
    return await response.json();
}

/**
 * Send message with files (using JSON for file content)
 * @param {string} message - User message
 * @param {string} conversationId - Optional conversation ID
 * @param {Array} fileData - Array of file objects with filename and base64 content
 * @returns {Promise<Object>} Response from agent
 */
async function sendMessageWithFiles(message, conversationId = null, fileData = []) {
    const response = await fetch(`${API_BASE}/${AGENT_ID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            conversation_id: conversationId,
            files: fileData,
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

/**
 * Convert file to base64
 * @param {File} file - File object
 * @returns {Promise<string>} Base64 encoded file content
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1]; // Remove data:...;base64, prefix
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

