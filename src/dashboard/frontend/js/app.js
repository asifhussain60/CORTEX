/**
 * Main App Initialization
 * Initializes CORTEX Neural Observatory
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('CORTEX Neural Observatory initialized');
    
    // Verify API connectivity
    api.get('/api/health')
        .then(response => {
            console.log('✓ Connected to API:', response);
        })
        .catch(error => {
            console.error('✗ Cannot connect to API backend:', error);
            console.log('Ensure FastAPI server is running: python -m src.dashboard.api.main');
        });
});
