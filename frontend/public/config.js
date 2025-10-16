/**
 * Runtime Configuration for API URL
 * This script runs before React initializes and sets the API URL dynamically
 * based on the current environment
 *
 * Supports:
 * - localhost development (http://localhost:3000)
 * - Network deployment (http://192.168.1.10:3000)
 * - Docker internal networking (http://frontend:3000)
 */

(function() {
    'use strict';

    // Determine the API URL based on the current hostname
    function getApiUrl() {
        const hostname = window.location.hostname;
        const port = window.location.port;

        console.log('[CONFIG] Detecting API URL for hostname:', hostname);

        // If running in Docker container internal network
        // (hostname will be 'frontend' or Docker internal IP like 172.x.x.x)
        if (hostname === 'frontend' || hostname.match(/^172\./)) {
            const apiUrl = 'http://backend:5000';
            console.log('[CONFIG] Docker internal network detected, using:', apiUrl);
            return apiUrl;
        }

        // For localhost or network access (192.168.x.x, 10.x.x.x, etc.)
        // Backend runs on same host as frontend, just different port
        const apiUrl = `http://${hostname}:5000`;
        console.log('[CONFIG] External access detected, using:', apiUrl);
        return apiUrl;
    }

    const apiUrl = getApiUrl();

    // Set as a global variable that React can read
    window.__API_URL__ = apiUrl;
    console.log('[CONFIG] API URL configured as:', apiUrl);
})();
