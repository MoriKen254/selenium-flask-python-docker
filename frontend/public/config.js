/**
 * Runtime Configuration for API URL
 * This script runs before React initializes and sets the API URL dynamically
 * based on the current environment (host machine vs Docker container)
 */

(function() {
    'use strict';

    // Determine the API URL based on the current hostname
    function getApiUrl() {
        const hostname = window.location.hostname;

        // If running in Docker container (hostname will be 'frontend' or an IP)
        // OR if accessed via 'frontend:3000', use Docker network name
        if (hostname === 'frontend' || hostname.match(/^172\./)) {
            return 'http://backend:5000';
        }

        // If accessed via localhost or 127.0.0.1 (host machine browser)
        // use localhost which maps to host's backend via port forwarding
        return 'http://localhost:5000';
    }

    const apiUrl = getApiUrl();

    // Set as a global variable that React can read
    window.__API_URL__ = apiUrl;
})();
