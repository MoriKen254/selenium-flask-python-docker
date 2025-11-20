"""Flask REST API for Todo List Application.

This module provides a RESTful API for managing todo items with full CRUD operations.
The API uses PostgreSQL for data persistence and supports CORS for frontend integration.
"""

from typing import Dict, Any, Tuple, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

from . import __version__


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """Application factory pattern for creating Flask app instances.

    Args:
        config: Optional configuration dictionary to override defaults.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    CORS(app)

    # Apply configuration
    if config:
        app.config.update(config)

    # Database configuration
    app.config.setdefault(
        'DATABASE_URL', 
        os.getenv('DATABASE_URL', 'postgresql://todouser:todopass@postgres:5432/tododb')
    )

    # Register routes
    register_routes(app)

    return app


def get_db_connection() -> psycopg2.extensions.connection:
    """Create and return a database connection with dictionary cursor.

    Returns:
        psycopg2.connection: PostgreSQL database connection with RealDictCursor factory.

    Note:
        The connection uses RealDictCursor to return results as dictionaries
        instead of tuples for easier JSON serialization.
    """
    database_url = os.getenv('DATABASE_URL', 'postgresql://todouser:todopass@postgres:5432/tododb')
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn


def serialize_datetime(obj: Any) -> Any:
    """Convert datetime objects to ISO format strings for JSON serialization.

    Args:
        obj: Any object, typically a datetime instance.

    Returns:
        str: ISO format datetime string if obj is datetime, otherwise returns obj unchanged.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 15, 10, 30, 0)
        >>> serialize_datetime(dt)
        '2024-01-15T10:30:00'
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def register_routes(app: Flask) -> None:
    """Register all API routes with the Flask application.

    Args:
        app: Flask application instance.
    """

    @app.route('/health', methods=['GET'])
    def health_check() -> Tuple[Dict[str, str], int]:
        """Health check endpoint to verify API and database connectivity.

        Returns:
            tuple: JSON response with status and HTTP status code.
                - 200: Service is healthy and database is connected
                - 500: Service is unhealthy with error details

        Response Schema:
            Success (200):
                {
                    "status": "healthy",
                    "database": "connected"
                }
            Error (500):
                {
                    "status": "unhealthy",
                    "error": "error message"
                }
        """
        try:
            conn = get_db_connection()
            conn.close()
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    @app.route('/api/todos', methods=['GET'])
    def get_todos() -> Tuple[Dict[str, Any], int]:
        """Retrieve all todos from the database ordered by creation date.

        Returns:
            tuple: JSON response with list of todos and HTTP status code.
                - 200: Successfully retrieved todos
                - 500: Server error with error message

        Response Schema:
            Success (200): Array of todo objects
                [
                    {
                        "id": 1,
                        "title": "Todo title",
                        "description": "Optional description",
                        "completed": false,
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": "2024-01-15T10:30:00"
                    }
                ]
            Error (500):
                {
                    "error": "error message"
                }
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM todos ORDER BY created_at DESC')
            todos = cur.fetchall()
            cur.close()
            conn.close()

            # Convert datetime objects to strings
            todos_list = []
            for todo in todos:
                todo_dict = dict(todo)
                todo_dict['created_at'] = serialize_datetime(todo_dict['created_at'])
                todo_dict['updated_at'] = serialize_datetime(todo_dict['updated_at'])
                todos_list.append(todo_dict)

            return jsonify(todos_list), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>', methods=['GET'])
    def get_todo(todo_id: int) -> Tuple[Dict[str, Any], int]:
        """Retrieve a specific todo by its ID.

        Args:
            todo_id (int): The unique identifier of the todo item.

        Returns:
            tuple: JSON response with todo object and HTTP status code.
                - 200: Successfully retrieved todo
                - 404: Todo not found
                - 500: Server error

        Response Schema:
            Success (200):
                {
                    "id": 1,
                    "title": "Todo title",
                    "description": "Description",
                    "completed": false,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                }
            Error (404/500):
                {
                    "error": "error message"
                }
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM todos WHERE id = %s', (todo_id,))
            todo = cur.fetchone()
            cur.close()
            conn.close()

            if todo is None:
                return jsonify({'error': 'Todo not found'}), 404

            todo_dict = dict(todo)
            todo_dict['created_at'] = serialize_datetime(todo_dict['created_at'])
            todo_dict['updated_at'] = serialize_datetime(todo_dict['updated_at'])

            return jsonify(todo_dict), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos', methods=['POST'])
    def create_todo() -> Tuple[Dict[str, Any], int]:
        """Create a new todo item.

        Request Body:
            {
                "title": "Todo title" (required),
                "description": "Optional description" (optional),
                "completed": false (optional, defaults to false)
            }

        Returns:
            tuple: JSON response with created todo and HTTP status code.
                - 201: Todo created successfully
                - 400: Invalid request (missing title)
                - 500: Server error

        Response Schema:
            Success (201):
                {
                    "id": 1,
                    "title": "New todo",
                    "description": "Description",
                    "completed": false,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                }
            Error (400/500):
                {
                    "error": "error message"
                }
        """
        try:
            data = request.get_json()

            if not data or 'title' not in data:
                return jsonify({'error': 'Title is required'}), 400

            title = data['title']
            description = data.get('description', '')
            completed = data.get('completed', False)

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO todos (title, description, completed) VALUES (%s, %s, %s) RETURNING *',
                (title, description, completed)
            )
            new_todo = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()

            todo_dict = dict(new_todo)
            todo_dict['created_at'] = serialize_datetime(todo_dict['created_at'])
            todo_dict['updated_at'] = serialize_datetime(todo_dict['updated_at'])

            return jsonify(todo_dict), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>', methods=['PUT'])
    def update_todo(todo_id: int) -> Tuple[Dict[str, Any], int]:
        """Update an existing todo item with partial or full updates.

        Args:
            todo_id (int): The unique identifier of the todo to update.

        Request Body:
            Any combination of:
            {
                "title": "Updated title" (optional),
                "description": "Updated description" (optional),
                "completed": true (optional)
            }

        Returns:
            tuple: JSON response with updated todo and HTTP status code.
                - 200: Todo updated successfully
                - 400: Invalid request (no data or no valid fields)
                - 404: Todo not found
                - 500: Server error

        Response Schema:
            Success (200):
                {
                    "id": 1,
                    "title": "Updated title",
                    "description": "Updated description",
                    "completed": true,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T11:00:00"
                }
            Error (400/404/500):
                {
                    "error": "error message"
                }
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            conn = get_db_connection()
            cur = conn.cursor()

            # Check if todo exists
            cur.execute('SELECT * FROM todos WHERE id = %s', (todo_id,))
            if cur.fetchone() is None:
                cur.close()
                conn.close()
                return jsonify({'error': 'Todo not found'}), 404

            # Build update query dynamically based on provided fields
            update_fields = []
            update_values = []

            if 'title' in data:
                update_fields.append('title = %s')
                update_values.append(data['title'])

            if 'description' in data:
                update_fields.append('description = %s')
                update_values.append(data['description'])

            if 'completed' in data:
                update_fields.append('completed = %s')
                update_values.append(data['completed'])

            if not update_fields:
                cur.close()
                conn.close()
                return jsonify({'error': 'No valid fields to update'}), 400

            update_values.append(todo_id)
            query = f"UPDATE todos SET {', '.join(update_fields)} WHERE id = %s RETURNING *"

            cur.execute(query, update_values)
            updated_todo = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()

            todo_dict = dict(updated_todo)
            todo_dict['created_at'] = serialize_datetime(todo_dict['created_at'])
            todo_dict['updated_at'] = serialize_datetime(todo_dict['updated_at'])

            return jsonify(todo_dict), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
    def delete_todo(todo_id: int) -> Tuple[Dict[str, Any], int]:
        """Delete a todo item permanently.

        Args:
            todo_id (int): The unique identifier of the todo to delete.

        Returns:
            tuple: JSON response with confirmation message and HTTP status code.
                - 200: Todo deleted successfully
                - 404: Todo not found
                - 500: Server error

        Response Schema:
            Success (200):
                {
                    "message": "Todo deleted successfully"
                }
            Error (404/500):
                {
                    "error": "error message"
                }
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Check if todo exists
            cur.execute('SELECT * FROM todos WHERE id = %s', (todo_id,))
            if cur.fetchone() is None:
                cur.close()
                conn.close()
                return jsonify({'error': 'Todo not found'}), 404

            cur.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
            conn.commit()
            cur.close()
            conn.close()

            return jsonify({'message': 'Todo deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/', methods=['GET'])
    def root() -> Tuple[Dict[str, Any], int]:
        """API root endpoint providing service information and available endpoints.

        Returns:
            tuple: JSON response with API information and HTTP 200 status code.

        Response Schema:
            {
                "message": "Todo List API",
                "version": "1.0.0",
                "endpoints": {
                    "GET /health": "Health check",
                    "GET /api/todos": "Get all todos",
                    "GET /api/todos/:id": "Get a specific todo",
                    "POST /api/todos": "Create a new todo",
                    "PUT /api/todos/:id": "Update a todo",
                    "DELETE /api/todos/:id": "Delete a todo"
                }
            }
        """
        return jsonify({
            'message': 'Todo List API',
            'version': __version__,
            'endpoints': {
                'GET /health': 'Health check',
                'GET /api/todos': 'Get all todos',
                'GET /api/todos/:id': 'Get a specific todo',
                'POST /api/todos': 'Create a new todo',
                'PUT /api/todos/:id': 'Update a todo',
                'DELETE /api/todos/:id': 'Delete a todo'
            }
        }), 200


def main() -> None:
    """Entry point for direct script execution."""
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
