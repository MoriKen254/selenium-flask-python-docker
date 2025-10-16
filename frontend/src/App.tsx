/**
 * Todo List Application - Main Component
 *
 * A full-stack todo list application built with React, TypeScript, Flask, and PostgreSQL.
 * This component provides a complete CRUD interface for managing todo items with real-time
 * updates and error handling.
 *
 * @module App
 */

import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import './App.css';
import { Todo, NewTodo, UpdateTodo } from './types/todo';

// Use runtime configuration if available, fall back to build-time env var, then default
declare global {
  interface Window {
    /** Runtime API URL configuration injected by config.js */
    __API_URL__?: string;
  }
}

/**
 * Main application component for the Todo List.
 *
 * Manages the complete todo lifecycle including creation, reading, updating, and deletion.
 * Uses dynamic API URL configuration to support both development and Docker environments.
 *
 * @component
 * @returns {React.FC} The rendered todo list application
 *
 * @example
 * ```tsx
 * import App from './App';
 *
 * function Root() {
 *   return <App />;
 * }
 * ```
 */
const App: React.FC = () => {
  /**
   * API URL determined at runtime from window.__API_URL__, environment variable, or default.
   * This allows the same build to work in different environments (localhost, Docker, etc.)
   */
  const API_URL: string = React.useMemo(() => {
    const runtimeApiUrl = (window as any)['__API_URL__'];
    const buildTimeApiUrl = process.env.REACT_APP_API_URL;
    return runtimeApiUrl || buildTimeApiUrl || 'http://localhost:5000';
  }, []);

  /** Array of all todos */
  const [todos, setTodos] = useState<Todo[]>([]);

  /** Data for new todo being created */
  const [newTodo, setNewTodo] = useState<NewTodo>({ title: '', description: '' });

  /** Todo currently being edited, or null if none */
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);

  /** Loading state for async operations */
  const [loading, setLoading] = useState<boolean>(false);

  /** Error message to display, or null if no error */
  const [error, setError] = useState<string | null>(null);

  // Fetch all todos on component mount
  useEffect(() => {
    fetchTodos();
  }, []);

  /**
   * Fetches all todos from the backend API.
   *
   * Updates the todos state with the fetched data or sets an error message if the request fails.
   * Sets loading state during the fetch operation.
   *
   * @async
   * @function fetchTodos
   * @returns {Promise<void>}
   * @throws {Error} If the API request fails
   */
  const fetchTodos = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/todos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTodos(data);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'An unknown error occurred';
      setError('Failed to fetch todos. Please make sure the backend is running.');
      console.error('Error fetching todos:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Creates a new todo item by submitting the form.
   *
   * Validates that a title is provided, sends a POST request to the API,
   * and updates the local state with the new todo.
   *
   * @async
   * @function handleCreateTodo
   * @param {FormEvent<HTMLFormElement>} e - The form submission event
   * @returns {Promise<void>}
   */
  const handleCreateTodo = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!newTodo.title.trim()) {
      alert('Please enter a title');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newTodo),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTodos([data, ...todos]);
      setNewTodo({ title: '', description: '' });
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'An unknown error occurred';
      setError('Failed to create todo');
      console.error('Error creating todo:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Updates an existing todo with partial or full data.
   *
   * Sends a PUT request to update the todo and refreshes the local state.
   *
   * @async
   * @function handleUpdateTodo
   * @param {number} id - The ID of the todo to update
   * @param {UpdateTodo} updates - Object containing fields to update
   * @returns {Promise<void>}
   */
  const handleUpdateTodo = async (id: number, updates: UpdateTodo): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/todos/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTodos(todos.map(todo => todo.id === id ? data : todo));
      setEditingTodo(null);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'An unknown error occurred';
      setError('Failed to update todo');
      console.error('Error updating todo:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Toggles the completion status of a todo.
   *
   * @async
   * @function handleToggleComplete
   * @param {Todo} todo - The todo to toggle
   * @returns {Promise<void>}
   */
  const handleToggleComplete = async (todo: Todo): Promise<void> => {
    await handleUpdateTodo(todo.id, { completed: !todo.completed });
  };

  /**
   * Deletes a todo after user confirmation.
   *
   * Shows a confirmation dialog before permanently deleting the todo.
   *
   * @async
   * @function handleDeleteTodo
   * @param {number} id - The ID of the todo to delete
   * @returns {Promise<void>}
   */
  const handleDeleteTodo = async (id: number): Promise<void> => {
    if (!window.confirm('Are you sure you want to delete this todo?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/todos/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setTodos(todos.filter(todo => todo.id !== id));
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : 'An unknown error occurred';
      setError('Failed to delete todo');
      console.error('Error deleting todo:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Save edited todo
  const handleSaveEdit = (todo: Todo): void => {
    handleUpdateTodo(todo.id, {
      title: todo.title,
      description: todo.description
    });
  };

  // Handle input change for new todo
  const handleNewTodoChange = (field: keyof NewTodo, value: string): void => {
    setNewTodo({ ...newTodo, [field]: value });
  };

  // Handle input change for editing todo
  const handleEditingTodoChange = (field: keyof Pick<Todo, 'title' | 'description'>, value: string): void => {
    if (editingTodo) {
      setEditingTodo({ ...editingTodo, [field]: value });
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="app-header">
          <h1>Todo List Application</h1>
          <p className="subtitle">Full-stack React + TypeScript + Flask + PostgreSQL</p>
        </header>

        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)} className="close-btn">×</button>
          </div>
        )}

        {/* Create Todo Form */}
        <form onSubmit={handleCreateTodo} className="create-form">
          <div className="form-group">
            <input
              type="text"
              placeholder="Todo title..."
              value={newTodo.title}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleNewTodoChange('title', e.target.value)}
              className="input-field"
              disabled={loading}
            />
            <textarea
              placeholder="Description (optional)..."
              value={newTodo.description}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => handleNewTodoChange('description', e.target.value)}
              className="textarea-field"
              rows={2}
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Adding...' : 'Add Todo'}
          </button>
        </form>

        {/* Todo List */}
        <div className="todos-container">
          {loading && todos.length === 0 ? (
            <div className="loading">Loading todos...</div>
          ) : todos.length === 0 ? (
            <div className="empty-state">
              <p>No todos yet. Create your first todo above!</p>
            </div>
          ) : (
            <div className="todos-list">
              {todos.map((todo: Todo) => (
                <div key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
                  {editingTodo?.id === todo.id ? (
                    // Edit mode
                    <div className="edit-form">
                      <input
                        type="text"
                        value={editingTodo.title}
                        onChange={(e: ChangeEvent<HTMLInputElement>) => handleEditingTodoChange('title', e.target.value)}
                        className="input-field"
                      />
                      <textarea
                        value={editingTodo.description}
                        onChange={(e: ChangeEvent<HTMLTextAreaElement>) => handleEditingTodoChange('description', e.target.value)}
                        className="textarea-field"
                        rows={2}
                      />
                      <div className="button-group">
                        <button
                          onClick={() => handleSaveEdit(editingTodo)}
                          className="btn btn-success"
                          disabled={loading}
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingTodo(null)}
                          className="btn btn-secondary"
                          disabled={loading}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    // View mode
                    <>
                      <div className="todo-content">
                        <div className="checkbox-wrapper">
                          <input
                            type="checkbox"
                            checked={todo.completed}
                            onChange={() => handleToggleComplete(todo)}
                            className="checkbox"
                            disabled={loading}
                          />
                        </div>
                        <div className="todo-text">
                          <h3 className="todo-title">{todo.title}</h3>
                          {todo.description && (
                            <p className="todo-description">{todo.description}</p>
                          )}
                          <span className="todo-date">
                            Created: {new Date(todo.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div className="todo-actions">
                        <button
                          onClick={() => setEditingTodo(todo)}
                          className="btn btn-edit"
                          disabled={loading}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteTodo(todo.id)}
                          className="btn btn-delete"
                          disabled={loading}
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Stats */}
        {todos.length > 0 && (
          <div className="stats">
            <span>Total: {todos.length}</span>
            <span>Completed: {todos.filter((t: Todo) => t.completed).length}</span>
            <span>Pending: {todos.filter((t: Todo) => !t.completed).length}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
