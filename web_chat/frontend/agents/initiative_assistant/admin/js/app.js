/* Admin Application Logic */

let currentInitiatives = [];
let currentInitiativeId = null;

// DOM Elements
const elements = {
    loginScreen: document.getElementById('login-screen'),
    adminInterface: document.getElementById('admin-interface'),
    loginForm: document.getElementById('login-form'),
    passwordInput: document.getElementById('password'),
    loginError: document.getElementById('login-error'),
    logoutBtn: document.getElementById('logout-btn'),
    initiativesList: document.getElementById('initiatives-list'),
    loadingIndicator: document.getElementById('loading-indicator'),
    noInitiatives: document.getElementById('no-initiatives'),
    searchInput: document.getElementById('search-input'),
    statusFilter: document.getElementById('status-filter'),
    totalInitiatives: document.getElementById('total-initiatives'),
    proposedInitiatives: document.getElementById('proposed-initiatives'),
    inProgressInitiatives: document.getElementById('in-progress-initiatives'),
    completedInitiatives: document.getElementById('completed-initiatives'),
    initiativeModal: document.getElementById('initiative-modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.getElementById('modal-close'),
    saveInitiativeBtn: document.getElementById('save-initiative-btn'),
    deleteInitiativeBtn: document.getElementById('delete-initiative-btn'),
    cancelModalBtn: document.getElementById('cancel-modal-btn')
};

/**
 * Initialize application
 */
async function init() {
    // Check if user is already logged in
    const token = typeof getSessionToken === 'function' ? getSessionToken() : null;
    if (token) {
        // Verify token by trying to fetch initiatives
        try {
            await loadInitiatives();
            showAdminInterface();
        } catch (error) {
            // Token invalid, show login
            clearSessionToken();
            showLoginScreen();
        }
    } else {
        showLoginScreen();
    }
    
    // Event listeners
    elements.loginForm.addEventListener('submit', handleLogin);
    elements.logoutBtn.addEventListener('click', handleLogout);
    elements.searchInput.addEventListener('input', filterInitiatives);
    elements.statusFilter.addEventListener('change', filterInitiatives);
    elements.modalClose.addEventListener('click', closeModal);
    elements.cancelModalBtn.addEventListener('click', closeModal);
    elements.saveInitiativeBtn.addEventListener('click', handleSaveInitiative);
    elements.deleteInitiativeBtn.addEventListener('click', handleDeleteInitiative);
    
    // Close modal on outside click
    elements.initiativeModal.addEventListener('click', (e) => {
        if (e.target === elements.initiativeModal) {
            closeModal();
        }
    });
}

/**
 * Show login screen
 */
function showLoginScreen() {
    elements.loginScreen.style.display = 'flex';
    elements.adminInterface.style.display = 'none';
}

/**
 * Show admin interface
 */
function showAdminInterface() {
    elements.loginScreen.style.display = 'none';
    elements.adminInterface.style.display = 'block';
}

/**
 * Handle login
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const password = elements.passwordInput.value;
    elements.loginError.style.display = 'none';
    
    try {
        const result = await login(password);
        
        if (result.success) {
            showAdminInterface();
            await loadInitiatives();
            elements.passwordInput.value = '';
        } else {
            elements.loginError.textContent = result.error || 'Kirjautuminen epäonnistui';
            elements.loginError.style.display = 'block';
        }
    } catch (error) {
        elements.loginError.textContent = 'Virhe kirjautumisessa. Yritä uudelleen.';
        elements.loginError.style.display = 'block';
    }
}

/**
 * Handle logout
 */
async function handleLogout() {
    if (confirm('Haluatko varmasti kirjautua ulos?')) {
        try {
            await logout();
        } catch (error) {
            // Ignore errors, clear token anyway
        }
        showLoginScreen();
    }
}

/**
 * Load initiatives from API
 */
async function loadInitiatives() {
    elements.loadingIndicator.style.display = 'block';
    elements.initiativesList.innerHTML = '';
    elements.noInitiatives.style.display = 'none';
    
    try {
        const result = await getInitiatives();
        
        if (result.success) {
            currentInitiatives = result.initiatives || [];
            updateStats();
            renderInitiatives(currentInitiatives);
        }
    } catch (error) {
        console.error('Error loading initiatives:', error);
        elements.initiativesList.innerHTML = '<div class="error-message">Virhe aloitteiden lataamisessa.</div>';
    } finally {
        elements.loadingIndicator.style.display = 'none';
    }
}

/**
 * Update statistics
 */
function updateStats() {
    const total = currentInitiatives.length;
    const proposed = currentInitiatives.filter(i => i.status === 'proposed').length;
    const inProgress = currentInitiatives.filter(i => i.status === 'in_progress').length;
    const completed = currentInitiatives.filter(i => i.status === 'completed').length;
    
    elements.totalInitiatives.textContent = total;
    elements.proposedInitiatives.textContent = proposed;
    elements.inProgressInitiatives.textContent = inProgress;
    elements.completedInitiatives.textContent = completed;
}

/**
 * Render initiatives list
 */
function renderInitiatives(initiatives) {
    if (initiatives.length === 0) {
        elements.noInitiatives.style.display = 'block';
        return;
    }
    
    elements.initiativesList.innerHTML = initiatives.map(initiative => `
        <div class="initiative-card" data-id="${initiative.id}">
            <div class="initiative-header">
                <div>
                    <div class="initiative-title">${escapeHtml(initiative.title)}</div>
                    <span class="initiative-status status-${initiative.status}">
                        ${getStatusLabel(initiative.status)}
                    </span>
                </div>
            </div>
            <div class="initiative-description">${escapeHtml(initiative.description || 'Ei kuvausta')}</div>
            <div class="initiative-meta">
                <div class="initiative-meta-item">
                    <strong>Luonut:</strong> ${escapeHtml(initiative.creator_name || 'Tuntematon')}
                </div>
                ${initiative.creator_department ? `
                    <div class="initiative-meta-item">
                        <strong>Osasto:</strong> ${escapeHtml(initiative.creator_department)}
                    </div>
                ` : ''}
                <div class="initiative-meta-item">
                    <strong>Luotu:</strong> ${formatDate(initiative.created_at)}
                </div>
            </div>
        </div>
    `).join('');
    
    // Add click listeners
    document.querySelectorAll('.initiative-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = parseInt(card.dataset.id);
            openInitiativeModal(id);
        });
    });
}

/**
 * Filter initiatives
 */
function filterInitiatives() {
    const searchTerm = elements.searchInput.value.toLowerCase();
    const statusFilter = elements.statusFilter.value;
    
    let filtered = currentInitiatives;
    
    if (searchTerm) {
        filtered = filtered.filter(init => 
            init.title.toLowerCase().includes(searchTerm) ||
            (init.description && init.description.toLowerCase().includes(searchTerm)) ||
            (init.creator_name && init.creator_name.toLowerCase().includes(searchTerm))
        );
    }
    
    if (statusFilter) {
        filtered = filtered.filter(init => init.status === statusFilter);
    }
    
    renderInitiatives(filtered);
}

/**
 * Open initiative detail modal
 */
async function openInitiativeModal(id) {
    currentInitiativeId = id;
    
    try {
        const result = await getInitiative(id);
        
        if (result.success) {
            const initiative = result.initiative;
            elements.modalTitle.textContent = `Aloite: ${escapeHtml(initiative.title)}`;
            
            elements.modalBody.innerHTML = `
                <form id="initiative-form" class="initiative-detail-form">
                    <div class="initiative-detail-row">
                        <div class="initiative-detail-label">Otsikko:</div>
                        <div class="initiative-detail-value">
                            <input type="text" id="edit-title" value="${escapeHtml(initiative.title)}" required>
                        </div>
                    </div>
                    <div class="initiative-detail-row">
                        <div class="initiative-detail-label">Kuvaus:</div>
                        <div class="initiative-detail-value">
                            <textarea id="edit-description" required>${escapeHtml(initiative.description || '')}</textarea>
                        </div>
                    </div>
                    <div class="initiative-detail-row">
                        <div class="initiative-detail-label">Tila:</div>
                        <div class="initiative-detail-value">
                            <select id="edit-status">
                                <option value="proposed" ${initiative.status === 'proposed' ? 'selected' : ''}>Ehdotettu</option>
                                <option value="in_progress" ${initiative.status === 'in_progress' ? 'selected' : ''}>Käynnissä</option>
                                <option value="completed" ${initiative.status === 'completed' ? 'selected' : ''}>Valmis</option>
                                <option value="cancelled" ${initiative.status === 'cancelled' ? 'selected' : ''}>Peruutettu</option>
                            </select>
                        </div>
                    </div>
                    <div class="initiative-detail-row">
                        <div class="initiative-detail-label">Luonut:</div>
                        <div class="initiative-detail-value">${escapeHtml(initiative.creator_name || 'Tuntematon')}</div>
                    </div>
                    ${initiative.creator_department ? `
                        <div class="initiative-detail-row">
                            <div class="initiative-detail-label">Osasto:</div>
                            <div class="initiative-detail-value">${escapeHtml(initiative.creator_department)}</div>
                        </div>
                    ` : ''}
                    ${initiative.creator_email ? `
                        <div class="initiative-detail-row">
                            <div class="initiative-detail-label">Sähköposti:</div>
                            <div class="initiative-detail-value">${escapeHtml(initiative.creator_email)}</div>
                        </div>
                    ` : ''}
                    ${initiative.goals ? `
                        <div class="initiative-detail-row">
                            <div class="initiative-detail-label">Tavoitteet:</div>
                            <div class="initiative-detail-value">${escapeHtml(initiative.goals)}</div>
                        </div>
                    ` : ''}
                    ${initiative.expected_outcomes ? `
                        <div class="initiative-detail-row">
                            <div class="initiative-detail-label">Odotetut tulokset:</div>
                            <div class="initiative-detail-value">${escapeHtml(initiative.expected_outcomes)}</div>
                        </div>
                    ` : ''}
                    <div class="initiative-detail-row">
                        <div class="initiative-detail-label">Luotu:</div>
                        <div class="initiative-detail-value">${formatDate(initiative.created_at)}</div>
                    </div>
                    ${initiative.updated_at ? `
                        <div class="initiative-detail-row">
                            <div class="initiative-detail-label">Päivitetty:</div>
                            <div class="initiative-detail-value">${formatDate(initiative.updated_at)}</div>
                        </div>
                    ` : ''}
                </form>
            `;
            
            elements.initiativeModal.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error loading initiative:', error);
        alert('Virhe aloitteen lataamisessa.');
    }
}

/**
 * Close modal
 */
function closeModal() {
    elements.initiativeModal.style.display = 'none';
    currentInitiativeId = null;
}

/**
 * Handle save initiative
 */
async function handleSaveInitiative() {
    if (!currentInitiativeId) return;
    
    const title = document.getElementById('edit-title').value;
    const description = document.getElementById('edit-description').value;
    const status = document.getElementById('edit-status').value;
    
    if (!title || !description) {
        alert('Otsikko ja kuvaus ovat pakollisia.');
        return;
    }
    
    try {
        const result = await updateInitiative(currentInitiativeId, {
            title,
            description,
            status
        });
        
        if (result.success) {
            alert('Aloite tallennettu onnistuneesti!');
            closeModal();
            await loadInitiatives();
        } else {
            alert('Virhe tallennuksessa: ' + (result.error || 'Tuntematon virhe'));
        }
    } catch (error) {
        console.error('Error saving initiative:', error);
        alert('Virhe tallennuksessa.');
    }
}

/**
 * Handle delete initiative
 */
async function handleDeleteInitiative() {
    if (!currentInitiativeId) return;
    
    if (!confirm('Haluatko varmasti poistaa tämän aloitteen? Tätä toimintoa ei voi perua.')) {
        return;
    }
    
    try {
        const result = await deleteInitiative(currentInitiativeId);
        
        if (result.success) {
            alert('Aloite poistettu onnistuneesti!');
            closeModal();
            await loadInitiatives();
        } else {
            alert('Virhe poistamisessa: ' + (result.error || 'Tuntematon virhe'));
        }
    } catch (error) {
        console.error('Error deleting initiative:', error);
        alert('Virhe poistamisessa.');
    }
}

/**
 * Get status label in Finnish
 */
function getStatusLabel(status) {
    const labels = {
        'proposed': 'Ehdotettu',
        'in_progress': 'Käynnissä',
        'completed': 'Valmis',
        'cancelled': 'Peruutettu'
    };
    return labels[status] || status;
}

/**
 * Format date
 */
function formatDate(dateString) {
    if (!dateString) return 'Tuntematon';
    const date = new Date(dateString);
    return date.toLocaleDateString('fi-FI', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

