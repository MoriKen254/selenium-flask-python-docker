import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import axios, { AxiosError } from 'axios';
import './App.css';
import { Todo, NewTodo, UpdateTodo } from './types/todo';

const API_URL: string = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const App: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState<NewTodo>({ title: '', description: '' });
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all todos
  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<Todo[]>(`${API_URL}/api/todos`);
      setTodos(response.data);
    } catch (err) {
      const errorMessage = err instanceof AxiosError
        ? err.message
        : 'An unknown error occurred';
      setError('Failed to fetch todos. Please make sure the backend is running.');
      console.error('Error fetching todos:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Create a new todo
  const handleCreateTodo = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!newTodo.title.trim()) {
      alert('Please enter a title');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post<Todo>(`${API_URL}/api/todos`, newTodo);
      setTodos([response.data, ...todos]);
      setNewTodo({ title: '', description: '' });
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof AxiosError
        ? err.message
        : 'An unknown error occurred';
      setError('Failed to create todo');
      console.error('Error creating todo:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Update a todo
  const handleUpdateTodo = async (id: number, updates: UpdateTodo): Promise<void> => {
    setLoading(true);
    try {
      const response = await axios.put<Todo>(`${API_URL}/api/todos/${id}`, updates);
      setTodos(todos.map(todo => todo.id === id ? response.data : todo));
      setEditingTodo(null);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof AxiosError
        ? err.message
        : 'An unknown error occurred';
      setError('Failed to update todo');
      console.error('Error updating todo:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Toggle todo completion
  const handleToggleComplete = async (todo: Todo): Promise<void> => {
    await handleUpdateTodo(todo.id, { completed: !todo.completed });
  };

  // Delete a todo
  const handleDeleteTodo = async (id: number): Promise<void> => {
    if (!window.confirm('Are you sure you want to delete this todo?')) {
      return;
    }

    setLoading(true);
    try {
      await axios.delete(`${API_URL}/api/todos/${id}`);
      setTodos(todos.filter(todo => todo.id !== id));
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof AxiosError
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
