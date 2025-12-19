// Configuration for deployment
const config = {
    // API URL - will be different in production
    API_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:5000'
        : 'https://disciplined-embrace-production-9079.up.railway.app', // Railway backend

    // OAuth redirect - automatically uses current domain
    OAUTH_REDIRECT: window.location.origin + '/auth/google/callback',

    // App settings
    APP_NAME: 'ARIA',
    VERSION: '1.0.0'
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = config;
}
