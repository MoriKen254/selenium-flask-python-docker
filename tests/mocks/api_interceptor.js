/**
 * API Interceptor for Unit Testing
 * This script intercepts and mocks API calls for testing without a backend
 * Uses synchronous mocking to avoid timing issues
 */

(function() {
    'use strict';

    console.log('[MOCK] Initializing API Interceptor...');

    // Mock data storage
    let mockTodos = [
        {
            id: 1,
            title: "Mock Todo 1",
            description: "This is a mocked todo for testing",
            completed: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        },
        {
            id: 2,
            title: "Mock Todo 2",
            description: "Another mocked todo",
            completed: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        }
    ];

    let nextId = 3;

    // Mock delay (in milliseconds)
    const mockDelay = window.__MOCK_DELAY__ || 50;

    // Process mock request and return result
    function processMockRequest(method, path, body) {
        console.log(`[MOCK] ${method} ${path}`);

        // Match route
        if (path === '/api/todos') {
            if (method === 'GET') {
                return { status: 200, data: [...mockTodos] };
            } else if (method === 'POST') {
                const newTodo = {
                    id: nextId++,
                    title: body.title || '',
                    description: body.description || '',
                    completed: body.completed || false,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                };
                mockTodos.unshift(newTodo);
                return { status: 201, data: newTodo };
            }
        } else if (path.match(/^\/api\/todos\/(\d+)$/)) {
            const id = parseInt(path.match(/^\/api\/todos\/(\d+)$/)[1]);
            const index = mockTodos.findIndex(t => t.id === id);

            if (method === 'GET') {
                if (index !== -1) {
                    return { status: 200, data: mockTodos[index] };
                }
                return { status: 404, data: { error: 'Todo not found' } };
            } else if (method === 'PUT') {
                if (index !== -1) {
                    mockTodos[index] = {
                        ...mockTodos[index],
                        ...body,
                        updated_at: new Date().toISOString()
                    };
                    return { status: 200, data: mockTodos[index] };
                }
                return { status: 404, data: { error: 'Todo not found' } };
            } else if (method === 'DELETE') {
                if (index !== -1) {
                    mockTodos.splice(index, 1);
                    return { status: 200, data: { message: 'Todo deleted successfully' } };
                }
                return { status: 404, data: { error: 'Todo not found' } };
            }
        } else if (path === '/health') {
            if (method === 'GET') {
                return { status: 200, data: { status: 'healthy', database: 'mocked' } };
            }
        }

        // Not mocked
        return null;
    }

    // Extract path from URL
    function extractPath(url) {
        if (url.startsWith('http')) {
            try {
                return new URL(url).pathname;
            } catch (e) {
                return url;
            }
        }
        return url;
    }

    // ============================================
    // INTERCEPT XMLHttpRequest (used by Axios)
    // ============================================
    const OriginalXHR = window.XMLHttpRequest;

    window.XMLHttpRequest = function() {
        const xhr = new OriginalXHR();
        let method, url;

        const originalOpen = xhr.open;
        const originalSend = xhr.send;
        const originalSetRequestHeader = xhr.setRequestHeader;

        let requestHeaders = {};

        xhr.setRequestHeader = function(name, value) {
            requestHeaders[name] = value;
            return originalSetRequestHeader.apply(this, arguments);
        };

        xhr.open = function(m, u) {
            method = m;
            url = u;
            return originalOpen.apply(this, arguments);
        };

        xhr.send = function(body) {
            const path = extractPath(url);
            const mockResult = processMockRequest(method, path, body ? JSON.parse(body) : {});

            if (mockResult) {
                // Mock the response
                console.log(`[MOCK] Returning mocked response for ${method} ${path}`);

                // Simulate async behavior with setTimeout
                setTimeout(() => {
                    try {
                        // Set readyState to 4 (DONE) first
                        Object.defineProperty(xhr, 'readyState', {
                            writable: true,
                            configurable: true,
                            value: 4
                        });

                        // Set status
                        Object.defineProperty(xhr, 'status', {
                            writable: true,
                            configurable: true,
                            value: mockResult.status
                        });

                        // Set statusText
                        Object.defineProperty(xhr, 'statusText', {
                            writable: true,
                            configurable: true,
                            value: mockResult.status >= 200 && mockResult.status < 300 ? 'OK' : 'Error'
                        });

                        // Set response and responseText
                        const responseData = JSON.stringify(mockResult.data);
                        Object.defineProperty(xhr, 'response', {
                            writable: true,
                            configurable: true,
                            value: responseData
                        });
                        Object.defineProperty(xhr, 'responseText', {
                            writable: true,
                            configurable: true,
                            value: responseData
                        });

                        // Set responseType
                        Object.defineProperty(xhr, 'responseType', {
                            writable: true,
                            configurable: true,
                            value: ''
                        });

                        // Set responseURL
                        Object.defineProperty(xhr, 'responseURL', {
                            writable: true,
                            configurable: true,
                            value: url
                        });

                        // Override header methods
                        xhr.getAllResponseHeaders = () => 'content-type: application/json\r\n';
                        xhr.getResponseHeader = (name) => {
                            if (name.toLowerCase() === 'content-type') {
                                return 'application/json';
                            }
                            return null;
                        };

                        // Create and dispatch events
                        const loadEvent = new ProgressEvent('load', {
                            lengthComputable: false,
                            loaded: 0,
                            total: 0
                        });

                        const loadEndEvent = new ProgressEvent('loadend', {
                            lengthComputable: false,
                            loaded: 0,
                            total: 0
                        });

                        // Trigger readystatechange event
                        if (xhr.onreadystatechange) {
                            xhr.onreadystatechange.call(xhr);
                        }

                        // Trigger load event
                        if (mockResult.status >= 200 && mockResult.status < 300) {
                            if (xhr.onload) {
                                xhr.onload.call(xhr, loadEvent);
                            }
                            // Dispatch load event for addEventListener
                            if (xhr.dispatchEvent) {
                                xhr.dispatchEvent(loadEvent);
                            }
                        } else {
                            // Trigger error for non-2xx responses
                            const errorEvent = new ProgressEvent('error');
                            if (xhr.onerror) {
                                xhr.onerror.call(xhr, errorEvent);
                            }
                            if (xhr.dispatchEvent) {
                                xhr.dispatchEvent(errorEvent);
                            }
                        }

                        // Trigger loadend event
                        if (xhr.onloadend) {
                            xhr.onloadend.call(xhr, loadEndEvent);
                        }
                        if (xhr.dispatchEvent) {
                            xhr.dispatchEvent(loadEndEvent);
                        }
                    } catch (e) {
                        console.error('[MOCK] Error setting up XHR response:', e);
                    }
                }, mockDelay);

                return;
            }

            // Not mocked, use real XHR
            return originalSend.apply(this, arguments);
        };

        return xhr;
    };

    // Copy static properties
    for (const prop in OriginalXHR) {
        if (OriginalXHR.hasOwnProperty(prop)) {
            try {
                window.XMLHttpRequest[prop] = OriginalXHR[prop];
            } catch (e) {
                // Ignore read-only properties
            }
        }
    }

    // ============================================
    // INTERCEPT fetch API (backup)
    // ============================================
    const originalFetch = window.fetch;

    window.fetch = function(url, options = {}) {
        const path = extractPath(url);
        const method = options.method || 'GET';
        const body = options.body ? JSON.parse(options.body) : {};

        const mockResult = processMockRequest(method, path, body);

        if (mockResult) {
            console.log(`[MOCK] Returning mocked fetch response for ${method} ${path}`);

            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        ok: mockResult.status >= 200 && mockResult.status < 300,
                        status: mockResult.status,
                        statusText: mockResult.status >= 200 && mockResult.status < 300 ? 'OK' : 'Error',
                        headers: new Headers({ 'Content-Type': 'application/json' }),
                        json: async () => mockResult.data,
                        text: async () => JSON.stringify(mockResult.data),
                        clone: function() { return this; }
                    });
                }, mockDelay);
            });
        }

        // Not mocked, use real fetch
        return originalFetch.apply(this, arguments);
    };

    // ============================================
    // Test API for programmatic control
    // ============================================
    window.__TEST_API__ = {
        resetMockData: function() {
            mockTodos = [
                {
                    id: 1,
                    title: "Mock Todo 1",
                    description: "This is a mocked todo for testing",
                    completed: false,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                },
                {
                    id: 2,
                    title: "Mock Todo 2",
                    description: "Another mocked todo",
                    completed: true,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                }
            ];
            nextId = 3;
        },
        setMockData: function(data) {
            mockTodos = data;
            nextId = Math.max(...mockTodos.map(t => t.id), 0) + 1;
        },
        getMockData: function() {
            return [...mockTodos];
        },
        addMockTodo: function(todo) {
            const newTodo = {
                id: nextId++,
                ...todo,
                created_at: todo.created_at || new Date().toISOString(),
                updated_at: todo.updated_at || new Date().toISOString()
            };
            mockTodos.push(newTodo);
            return newTodo;
        }
    };

    window.__API_MOCKING_ENABLED__ = true;
    console.log('[MOCK] API Interceptor loaded successfully');
    console.log('[MOCK] Mock todos available:', mockTodos.length);
})();
