from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://todouser:todopass@postgres:5432/tododb')

def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def serialize_datetime(obj):
    """Convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# GET all todos
@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Retrieve all todos from the database"""
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

# GET single todo by ID
@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Retrieve a specific todo by ID"""
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

# POST create a new todo
@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo item"""
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

# PUT update a todo
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo item"""
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

# DELETE a todo
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item"""
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

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """API root endpoint"""
    return jsonify({
        'message': 'Todo List API',
        'version': '1.0',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /api/todos': 'Get all todos',
            'GET /api/todos/:id': 'Get a specific todo',
            'POST /api/todos': 'Create a new todo',
            'PUT /api/todos/:id': 'Update a todo',
            'DELETE /api/todos/:id': 'Delete a todo'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
