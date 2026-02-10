// Main application script for the CORTEX documentation site.
// Handles role selection, tab navigation, and delegates rendering
// to visualization functions defined in visualizations.js.

window.CORTEX_APP = {
    currentRole: 'leader',
    currentTab: 'overview',
    // map roles to recommended tab order (could be extended)
    rolePaths: {
        leader: ['overview','capabilities','architecture','security','ops','next'],
        po: ['overview','capabilities','architecture','intelligence','wiring','next'],
        manager: ['overview','capabilities','wiring','quality','ops','next'],
        engineer: ['overview','architecture','intelligence','wiring','quality','ops','next'],
        quality: ['overview','quality','security','wiring','next']
    }
};

// Utility to set the active tab and call its renderer
function setActiveTab(tabName) {
    window.CORTEX_APP.currentTab = tabName;
    // update tab buttons
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    // show corresponding content container
    const sections = document.querySelectorAll('.tab-content');
    sections.forEach(sec => {
        sec.classList.remove('active');
    });
    const container = document.getElementById(tabName);
    container.classList.add('active');
    // invoke renderer
    const renderer = window.CORTEX_VIZ[tabName];
    if (typeof renderer === 'function') {
        renderer(container);
    }
}

// Initialise app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('role-overlay');
    const mainContainer = document.getElementById('main-container');
    const roleLabel = document.getElementById('role-label');
    // Role selection
    document.querySelectorAll('.role-card').forEach(card => {
        card.addEventListener('click', () => {
            const roleKey = card.getAttribute('data-role');
            window.CORTEX_APP.currentRole = roleKey;
            // update nav to reflect role
            roleLabel.textContent = window.CORTEX_DATA.roles[roleKey].name;
            // hide overlay and show main
            overlay.classList.add('hidden');
            mainContainer.classList.remove('hidden');
            // default to first recommended tab for this role
            const path = window.CORTEX_APP.rolePaths[roleKey] || ['overview'];
            setActiveTab(path[0]);
        });
    });
    // Tab click handlers
    document.querySelectorAll('.tab').forEach(tabBtn => {
        tabBtn.addEventListener('click', () => {
            const name = tabBtn.getAttribute('data-tab');
            setActiveTab(name);
        });
    });
    // For users with JS disabled, the overlay remains; else we can automatically show once they select role
});