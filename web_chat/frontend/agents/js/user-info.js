/* User Info and Authentication Management */

/**
 * Fetch current user information from API
 * @returns {Promise<Object|null>} User info object or null if not authenticated
 */
async function getCurrentUser() {
    try {
        const response = await fetch('/auth/me', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            return null;
        }
        
        const data = await response.json();
        return data.success ? data.user : null;
    } catch (error) {
        console.error('Error fetching user info:', error);
        return null;
    }
}

/**
 * Logout user and redirect to home
 */
async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        // Redirect to home page after logout
        window.location.href = '/';
    } catch (error) {
        console.error('Error during logout:', error);
        // Still redirect even if logout fails
        window.location.href = '/';
    }
}

/**
 * Create user info UI element
 * @param {Object} user - User info object
 * @returns {HTMLElement} User info element
 */
function createUserInfoElement(user) {
    const userInfoContainer = document.createElement('div');
    userInfoContainer.className = 'user-info';
    
    const userName = user.name || user.email || user.preferred_username || 'User';
    const userEmail = user.email || user.preferred_username || '';
    
    userInfoContainer.innerHTML = `
        <div class="user-info__details">
            <span class="user-info__name">${escapeHtml(userName)}</span>
            ${userEmail ? `<span class="user-info__email">${escapeHtml(userEmail)}</span>` : ''}
        </div>
        <button class="user-info__logout" onclick="logout()" aria-label="Logout">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 3h4a2 2 0 012 2v10a2 2 0 01-2 2h-4M8 7l4-4m0 0l4 4m-4-4v12"/>
            </svg>
            <span>Kirjaudu ulos</span>
        </button>
    `;
    
    return userInfoContainer;
}

/**
 * Initialize user info in header
 */
async function initUserInfo() {
    const user = await getCurrentUser();
    
    if (!user) {
        // If no user, redirect to login
        window.location.href = '/auth/login?redirect=' + encodeURIComponent(window.location.pathname);
        return;
    }
    
    // Find user info container or header element
    const userInfoContainer = document.getElementById('user-info-container');
    if (userInfoContainer) {
        userInfoContainer.appendChild(createUserInfoElement(user));
        return;
    }
    
    // Fallback: try to find header element
    const header = document.querySelector('.agent-list-header');
    if (header) {
        header.appendChild(createUserInfoElement(user));
        return;
    }
    
    // Last resort: try to find any header element
    const headers = document.querySelectorAll('header, .header, [class*="header"]');
    if (headers.length > 0) {
        headers[0].appendChild(createUserInfoElement(user));
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make logout function globally available
window.logout = logout;

// Initialize user info when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUserInfo);
} else {
    initUserInfo();
}

