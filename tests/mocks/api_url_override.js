/**
 * API URL Override for Integration Tests
 * This script overrides the API URL before React initializes
 * Allows integration tests to connect to backend via Docker network
 */

(function() {
    'use strict';

    console.log('[ENV_OVERRIDE] Setting API URL for integration tests');

    // Override process.env for React
    window.process = window.process || {};
    window.process.env = window.process.env || {};
    window.process.env.REACT_APP_API_URL = 'http://backend:5000';

    console.log('[ENV_OVERRIDE] API URL set to:', window.process.env.REACT_APP_API_URL);
})();
