/**
 * API Interceptor for Unit Testing
 * This script is injected into the browser to intercept and mock API calls
 * Only active when TEST_MODE=unit
 */

(function() {
    'use strict';

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

    // Helper to simulate network delay
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Mock API responses
    const mockResponses = {
        '/api/todos': {
            GET: async () => {
                await delay(window.__MOCK_DELAY__ || 100);
                return { status: 200, data: [...mockTodos] };
            },
            POST: async (body) => {
                await delay(window.__MOCK_DELAY__ || 100);
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
        },
        '/api/todos/:id': {
            GET: async (id) => {
                await delay(window.__MOCK_DELAY__ || 100);
                const todo = mockTodos.find(t => t.id === parseInt(id));
                if (todo) {
                    return { status: 200, data: todo };
                }
                return { status: 404, data: { error: 'Todo not found' } };
            },
            PUT: async (id, body) => {
                await delay(window.__MOCK_DELAY__ || 100);
                const index = mockTodos.findIndex(t => t.id === parseInt(id));
                if (index !== -1) {
                    mockTodos[index] = {
                        ...mockTodos[index],
                        ...body,
                        updated_at: new Date().toISOString()
                    };
                    return { status: 200, data: mockTodos[index] };
                }
                return { status: 404, data: { error: 'Todo not found' } };
            },
            DELETE: async (id) => {
                await delay(window.__MOCK_DELAY__ || 100);
                const index = mockTodos.findIndex(t => t.id === parseInt(id));
                if (index !== -1) {
                    mockTodos.splice(index, 1);
                    return { status: 200, data: { message: 'Todo deleted successfully' } };
                }
                return { status: 404, data: { error: 'Todo not found' } };
            }
        },
        '/health': {
            GET: async () => {
                await delay(window.__MOCK_DELAY__ || 100);
                return { status: 200, data: { status: 'healthy', database: 'mocked' } };
            }
        }
    };

    // Helper to match URL patterns
    function matchRoute(url) {
        for (const [pattern, methods] of Object.entries(mockResponses)) {
            const regex = new RegExp('^' + pattern.replace(':id', '(\\d+)') + '$');
            const match = url.match(regex);
            if (match) {
                return { methods, params: match.slice(1) };
            }
        }
        return null;
    }

    // Store original fetch
    const originalFetch = window.fetch;

    // Override fetch
    window.fetch = async function(url, options = {}) {
        // Extract the path from the URL
        let path = url;
        if (url.startsWith('http')) {
            try {
                const urlObj = new URL(url);
                path = urlObj.pathname;
            } catch (e) {
                path = url;
            }
        }

        // Check if this is an API call we should mock
        const route = matchRoute(path);

        if (route && window.__API_MOCKING_ENABLED__) {
            const method = options.method || 'GET';
            const handler = route.methods[method];

            if (handler) {
                console.log(`[MOCK] Intercepting ${method} ${path}`);

                try {
                    let result;
                    if (method === 'GET') {
                        result = await handler(...route.params);
                    } else if (method === 'POST' || method === 'PUT') {
                        const body = options.body ? JSON.parse(options.body) : {};
                        result = await handler(...route.params, body);
                    } else if (method === 'DELETE') {
                        result = await handler(...route.params);
                    }

                    // Return a mock Response object
                    return {
                        ok: result.status >= 200 && result.status < 300,
                        status: result.status,
                        statusText: result.status === 200 ? 'OK' : 'Error',
                        headers: new Headers({ 'Content-Type': 'application/json' }),
                        json: async () => result.data,
                        text: async () => JSON.stringify(result.data),
                        clone: function() { return this; }
                    };
                } catch (error) {
                    console.error('[MOCK] Error handling request:', error);
                    return {
                        ok: false,
                        status: 500,
                        statusText: 'Internal Server Error',
                        json: async () => ({ error: error.message })
                    };
                }
            }
        }

        // If not mocked, use original fetch
        return originalFetch.call(this, url, options);
    };

    // Store original XMLHttpRequest
    const OriginalXHR = window.XMLHttpRequest;

    // Override XMLHttpRequest for axios compatibility
    window.XMLHttpRequest = function() {
        const xhr = new OriginalXHR();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;

        let method, url;

        xhr.open = function(m, u, ...args) {
            method = m;
            url = u;
            return originalOpen.apply(this, [m, u, ...args]);
        };

        xhr.send = async function(body) {
            // Extract path from URL
            let path = url;
            if (url.startsWith('http')) {
                try {
                    const urlObj = new URL(url);
                    path = urlObj.pathname;
                } catch (e) {
                    path = url;
                }
            }

            const route = matchRoute(path);

            if (route && window.__API_MOCKING_ENABLED__) {
                const handler = route.methods[method];

                if (handler) {
                    console.log(`[MOCK] Intercepting XHR ${method} ${path}`);

                    try {
                        let result;
                        if (method === 'GET') {
                            result = await handler(...route.params);
                        } else if (method === 'POST' || method === 'PUT') {
                            const parsedBody = body ? JSON.parse(body) : {};
                            result = await handler(...route.params, parsedBody);
                        } else if (method === 'DELETE') {
                            result = await handler(...route.params);
                        }

                        // Simulate successful XHR response
                        Object.defineProperty(xhr, 'status', { value: result.status, writable: false });
                        Object.defineProperty(xhr, 'statusText', {
                            value: result.status === 200 ? 'OK' : 'Error',
                            writable: false
                        });
                        Object.defineProperty(xhr, 'response', {
                            value: JSON.stringify(result.data),
                            writable: false
                        });
                        Object.defineProperty(xhr, 'responseText', {
                            value: JSON.stringify(result.data),
                            writable: false
                        });
                        Object.defineProperty(xhr, 'readyState', { value: 4, writable: false });

                        // Trigger events
                        setTimeout(() => {
                            if (xhr.onreadystatechange) xhr.onreadystatechange();
                            if (xhr.onload) xhr.onload();
                        }, 0);

                        return;
                    } catch (error) {
                        console.error('[MOCK] Error handling XHR request:', error);
                    }
                }
            }

            // If not mocked, use original send
            return originalSend.apply(this, [body]);
        };

        return xhr;
    };

    // Expose API for tests to manipulate mock data
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

    console.log('[MOCK] API Interceptor loaded and active');
    window.__API_MOCKING_ENABLED__ = true;
})();
