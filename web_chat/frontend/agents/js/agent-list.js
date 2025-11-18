/* Agent Listing Page Logic */

/**
 * Load and display agents
 */
async function loadAgents() {
    const agentGrid = document.getElementById('agent-grid');
    
    try {
        const response = await fetch('/api/agents');
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load agents');
        }
        
        const agents = data.agents;
        
        if (agents.length === 0) {
            agentGrid.innerHTML = `
                <div class="agent-card">
                    <p>Ei saatavilla olevia agenteja.</p>
                </div>
            `;
            return;
        }
        
        // Add SharePoint File Browser card
        const sharepointCard = `
            <a href="sharepoint_browser/" class="agent-card">
                <div class="agent-card__header">
                    <h2 class="agent-card__title">SharePoint File Browser</h2>
                    <span class="agent-card__status agent-card__status--available">
                        Käytettävissä
                    </span>
                </div>
                <p class="agent-card__description">Selaa, lataa ja hallitse SharePoint-tiedostoja</p>
                <span class="agent-card__link">
                    Avaa tiedostoselain →
                </span>
            </a>
        `;
        
        const agentCards = agents.map(agent => `
            <a href="${agent.ui_path}" class="agent-card">
                <div class="agent-card__header">
                    <h2 class="agent-card__title">${escapeHtml(agent.name)}</h2>
                    <span class="agent-card__status agent-card__status--${agent.status}">
                        ${agent.status === 'available' ? 'Käytettävissä' : 'Ei käytössä'}
                    </span>
                </div>
                <p class="agent-card__description">${escapeHtml(agent.description || '')}</p>
                <span class="agent-card__link">
                    Avaa agentti →
                </span>
            </a>
        `).join('');
        
        agentGrid.innerHTML = sharepointCard + agentCards;
        
    } catch (error) {
        agentGrid.innerHTML = `
            <div class="agent-card">
                <p>Virhe agenteja ladatessa: ${escapeHtml(error.message)}</p>
            </div>
        `;
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load agents when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadAgents);
} else {
    loadAgents();
}

