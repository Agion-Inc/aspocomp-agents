/* API Client for communicating with backend */

const API_BASE_URL = 'http://localhost:5001/api';

/**
 * API client object
 */
const api = {
    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            if (!response.ok) {
                throw new Error(`Health check failed: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    },

    /**
     * Get available models
     */
    async getModels() {
        try {
            const response = await fetch(`${API_BASE_URL}/models`);
            if (!response.ok) {
                throw new Error(`Failed to get models: ${response.status}`);
            }
            const data = await response.json();
            return data.models || [];
        } catch (error) {
            console.error('Get models error:', error);
            throw error;
        }
    },

    /**
     * Send a message to the chat API
     */
    async sendMessage(message, options = {}) {
        try {
            const body = {
                message: message,
                model: options.model || 'gemini-2.5-flash',
                mcp_enabled: options.mcp_enabled || false,
            };
            
            if (options.conversation_id) {
                body.conversation_id = options.conversation_id;
            }
            
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                // Create error object with response data
                const error = new Error(data.error || `Request failed: ${response.status}`);
                error.response = data;
                error.status = response.status;
                throw error;
            }
            
            return data;
        } catch (error) {
            console.error('Send message error:', error);
            // Re-throw with more context if it's a fetch error
            if (error instanceof TypeError && error.message.includes('fetch')) {
                const networkError = new Error('Network error: Cannot connect to server');
                networkError.originalError = error;
                throw networkError;
            }
            throw error;
        }
    },

    /**
     * Clear conversation
     */
    async clearConversation(conversationId) {
        try {
            const response = await fetch(`${API_BASE_URL}/conversation/${conversationId}`, {
                method: 'DELETE',
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || `Failed to clear conversation: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Clear conversation error:', error);
            throw error;
        }
    },
};

