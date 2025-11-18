/* Admin API Client */

const API_BASE = '/admin/api';

/**
 * Get session token from cookie or storage
 */
function getSessionToken() {
    // Try to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'admin_session') {
            return value;
        }
    }
    return null;
}

/**
 * Set session token in cookie
 */
function setSessionToken(token) {
    document.cookie = `admin_session=${token}; path=/; max-age=86400; SameSite=Lax`;
}

/**
 * Clear session token
 */
function clearSessionToken() {
    document.cookie = 'admin_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
}

/**
 * Make authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
    const token = getSessionToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['X-Session-Token'] = token;
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        // Unauthorized - clear token and redirect to login
        clearSessionToken();
        window.location.reload();
        throw new Error('Authentication required');
    }
    
    return response.json();
}

/**
 * Login
 */
async function login(password) {
    const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
    });
    
    const data = await response.json();
    
    if (data.success && data.token) {
        setSessionToken(data.token);
    }
    
    return data;
}

/**
 * Logout
 */
async function logout() {
    try {
        await apiRequest('/logout', { method: 'POST' });
    } finally {
        clearSessionToken();
    }
}

/**
 * Get all initiatives
 */
async function getInitiatives() {
    return apiRequest('/initiatives');
}

/**
 * Get a specific initiative
 */
async function getInitiative(id) {
    return apiRequest(`/initiatives/${id}`);
}

/**
 * Update an initiative
 */
async function updateInitiative(id, data) {
    return apiRequest(`/initiatives/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

/**
 * Delete an initiative
 */
async function deleteInitiative(id) {
    return apiRequest(`/initiatives/${id}`, {
        method: 'DELETE'
    });
}

