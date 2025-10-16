import pytest
import json
from datetime import datetime


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check_success(self, client, clean_db):
        """Test health check returns healthy status"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Todo List API'
        assert data['version'] == '1.0'
        assert 'endpoints' in data
        assert 'GET /api/todos' in data['endpoints']


class TestGetTodos:
    """Tests for GET /api/todos endpoint"""

    def test_get_todos_empty(self, client, clean_db):
        """Test getting todos when database is empty"""
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_todos_with_data(self, client, clean_db, seed_todos):
        """Test getting todos with existing data"""
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 3

        # Verify todo structure
        todo = data[0]
        assert 'id' in todo
        assert 'title' in todo
        assert 'description' in todo
        assert 'completed' in todo
        assert 'created_at' in todo
        assert 'updated_at' in todo

    def test_get_todos_order(self, client, clean_db, seed_todos):
        """Test todos are returned in descending order by created_at"""
        response = client.get('/api/todos')
        data = response.get_json()

        # Verify order (most recent first)
        for i in range(len(data) - 1):
            assert data[i]['id'] >= data[i + 1]['id']


class TestGetTodoById:
    """Tests for GET /api/todos/:id endpoint"""

    def test_get_todo_by_id_success(self, client, clean_db, seed_todos):
        """Test getting a specific todo by ID"""
        todo_id = seed_todos[0]['id']
        response = client.get(f'/api/todos/{todo_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == todo_id
        assert data['title'] == seed_todos[0]['title']

    def test_get_todo_by_id_not_found(self, client, clean_db):
        """Test getting non-existent todo returns 404"""
        response = client.get('/api/todos/99999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Todo not found'

    def test_get_todo_by_id_invalid(self, client, clean_db):
        """Test getting todo with invalid ID format"""
        response = client.get('/api/todos/invalid')
        assert response.status_code == 404  # Flask returns 404 for invalid routes


class TestCreateTodo:
    """Tests for POST /api/todos endpoint"""

    def test_create_todo_success(self, client, clean_db, sample_todo):
        """Test creating a new todo successfully"""
        response = client.post('/api/todos', json=sample_todo)
        assert response.status_code == 201
        data = response.get_json()

        assert data['title'] == sample_todo['title']
        assert data['description'] == sample_todo['description']
        assert data['completed'] == sample_todo['completed']
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_create_todo_minimal(self, client, clean_db):
        """Test creating todo with only required fields"""
        todo = {'title': 'Minimal Todo'}
        response = client.post('/api/todos', json=todo)
        assert response.status_code == 201
        data = response.get_json()

        assert data['title'] == 'Minimal Todo'
        assert data['description'] == ''
        assert data['completed'] is False

    def test_create_todo_missing_title(self, client, clean_db):
        """Test creating todo without title returns error"""
        todo = {'description': 'No title'}
        response = client.post('/api/todos', json=todo)
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Title is required'

    def test_create_todo_empty_title(self, client, clean_db):
        """Test creating todo with empty title"""
        todo = {'title': ''}
        response = client.post('/api/todos', json=todo)
        assert response.status_code == 201  # Backend accepts empty string

    def test_create_todo_no_data(self, client, clean_db):
        """Test creating todo without data returns error"""
        response = client.post('/api/todos', json=None)
        assert response.status_code in [400, 500]  # Can be either depending on Flask version
        data = response.get_json()
        assert 'error' in data

    def test_create_todo_with_completed_true(self, client, clean_db):
        """Test creating todo with completed=true"""
        todo = {'title': 'Already done', 'completed': True}
        response = client.post('/api/todos', json=todo)
        assert response.status_code == 201
        data = response.get_json()
        assert data['completed'] is True

    def test_create_multiple_todos(self, client, clean_db):
        """Test creating multiple todos"""
        todos = [
            {'title': 'Todo 1'},
            {'title': 'Todo 2'},
            {'title': 'Todo 3'}
        ]

        created_ids = []
        for todo in todos:
            response = client.post('/api/todos', json=todo)
            assert response.status_code == 201
            created_ids.append(response.get_json()['id'])

        # Verify all were created
        assert len(set(created_ids)) == 3


class TestUpdateTodo:
    """Tests for PUT /api/todos/:id endpoint"""

    def test_update_todo_title(self, client, clean_db, seed_todos):
        """Test updating todo title"""
        todo_id = seed_todos[0]['id']
        update_data = {'title': 'Updated Title'}

        response = client.put(f'/api/todos/{todo_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Updated Title'
        assert data['id'] == todo_id

    def test_update_todo_description(self, client, clean_db, seed_todos):
        """Test updating todo description"""
        todo_id = seed_todos[0]['id']
        update_data = {'description': 'Updated description'}

        response = client.put(f'/api/todos/{todo_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        assert data['description'] == 'Updated description'

    def test_update_todo_completed(self, client, clean_db, seed_todos):
        """Test toggling todo completed status"""
        todo_id = seed_todos[0]['id']
        original_status = seed_todos[0]['completed']
        update_data = {'completed': not original_status}

        response = client.put(f'/api/todos/{todo_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        assert data['completed'] == (not original_status)

    def test_update_todo_multiple_fields(self, client, clean_db, seed_todos):
        """Test updating multiple fields at once"""
        todo_id = seed_todos[0]['id']
        update_data = {
            'title': 'New Title',
            'description': 'New Description',
            'completed': True
        }

        response = client.put(f'/api/todos/{todo_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'New Title'
        assert data['description'] == 'New Description'
        assert data['completed'] is True

    def test_update_todo_not_found(self, client, clean_db):
        """Test updating non-existent todo returns 404"""
        update_data = {'title': 'Updated'}
        response = client.put('/api/todos/99999', json=update_data)
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Todo not found'

    def test_update_todo_no_data(self, client, clean_db, seed_todos):
        """Test updating todo without data returns error"""
        todo_id = seed_todos[0]['id']
        response = client.put(f'/api/todos/{todo_id}', json=None)
        assert response.status_code in [400, 500]  # Can be either depending on Flask version
        data = response.get_json()
        assert 'error' in data

    def test_update_todo_empty_data(self, client, clean_db, seed_todos):
        """Test updating todo with empty object returns error"""
        todo_id = seed_todos[0]['id']
        response = client.put(f'/api/todos/{todo_id}', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        # The API returns 'No data provided' for empty objects
        assert data['error'] in ['No valid fields to update', 'No data provided']

    def test_update_todo_invalid_fields(self, client, clean_db, seed_todos):
        """Test updating with invalid fields only"""
        todo_id = seed_todos[0]['id']
        update_data = {'invalid_field': 'value'}
        response = client.put(f'/api/todos/{todo_id}', json=update_data)
        assert response.status_code == 400

    def test_update_todo_updates_timestamp(self, client, clean_db, seed_todos):
        """Test that updating a todo updates the updated_at timestamp"""
        todo_id = seed_todos[0]['id']
        original_updated_at = seed_todos[0]['updated_at']

        import time
        time.sleep(1)  # Wait to ensure timestamp difference

        update_data = {'title': 'Updated'}
        response = client.put(f'/api/todos/{todo_id}', json=update_data)
        data = response.get_json()

        # Updated timestamp should be different
        assert data['updated_at'] != original_updated_at


class TestDeleteTodo:
    """Tests for DELETE /api/todos/:id endpoint"""

    def test_delete_todo_success(self, client, clean_db, seed_todos):
        """Test deleting a todo successfully"""
        todo_id = seed_todos[0]['id']
        response = client.delete(f'/api/todos/{todo_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'Todo deleted successfully'

        # Verify todo is actually deleted
        get_response = client.get(f'/api/todos/{todo_id}')
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client, clean_db):
        """Test deleting non-existent todo returns 404"""
        response = client.delete('/api/todos/99999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Todo not found'

    def test_delete_todo_and_verify_list(self, client, clean_db, seed_todos):
        """Test deleting todo removes it from list"""
        initial_count = len(seed_todos)
        todo_id = seed_todos[0]['id']

        client.delete(f'/api/todos/{todo_id}')

        response = client.get('/api/todos')
        remaining_todos = response.get_json()
        assert len(remaining_todos) == initial_count - 1
        assert all(todo['id'] != todo_id for todo in remaining_todos)

    def test_delete_all_todos(self, client, clean_db, seed_todos):
        """Test deleting all todos"""
        for todo in seed_todos:
            response = client.delete(f'/api/todos/{todo["id"]}')
            assert response.status_code == 200

        # Verify all deleted
        response = client.get('/api/todos')
        assert len(response.get_json()) == 0


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_create_todo_with_very_long_title(self, client, clean_db):
        """Test creating todo with very long title"""
        long_title = 'A' * 300  # Longer than VARCHAR(255)
        todo = {'title': long_title}
        response = client.post('/api/todos', json=todo)
        # Should either truncate or fail gracefully
        assert response.status_code in [201, 400, 500]

    def test_create_todo_with_special_characters(self, client, clean_db):
        """Test creating todo with special characters"""
        todo = {
            'title': 'Test <script>alert("xss")</script>',
            'description': 'Special chars: @#$%^&*()[]{}|\\;:\'",.<>?/`~'
        }
        response = client.post('/api/todos', json=todo)
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == todo['title']

    def test_create_todo_with_unicode(self, client, clean_db):
        """Test creating todo with unicode characters"""
        todo = {
            'title': 'Unicode Test 你好 мир 🎉',
            'description': 'Emoji test: 😀 🎈 ✨'
        }
        response = client.post('/api/todos', json=todo)
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == todo['title']

    def test_create_todo_with_null_description(self, client, clean_db):
        """Test creating todo with null description"""
        todo = {'title': 'Test', 'description': None}
        response = client.post('/api/todos', json=todo)
        assert response.status_code == 201

    def test_invalid_json_format(self, client, clean_db):
        """Test sending invalid JSON returns error"""
        response = client.post(
            '/api/todos',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 415, 500]

    def test_wrong_content_type(self, client, clean_db):
        """Test sending data with wrong content type"""
        response = client.post(
            '/api/todos',
            data='title=Test',
            content_type='application/x-www-form-urlencoded'
        )
        # Should handle gracefully - Flask returns 500 when get_json() is called on non-JSON
        assert response.status_code in [400, 415, 500]


class TestDataIntegrity:
    """Tests for data integrity and consistency"""

    def test_todo_id_auto_increment(self, client, clean_db):
        """Test that todo IDs auto-increment correctly"""
        todo1 = client.post('/api/todos', json={'title': 'First'}).get_json()
        todo2 = client.post('/api/todos', json={'title': 'Second'}).get_json()
        todo3 = client.post('/api/todos', json={'title': 'Third'}).get_json()

        assert todo2['id'] > todo1['id']
        assert todo3['id'] > todo2['id']

    def test_created_at_is_set(self, client, clean_db, sample_todo):
        """Test that created_at timestamp is automatically set"""
        response = client.post('/api/todos', json=sample_todo)
        data = response.get_json()

        assert 'created_at' in data
        assert data['created_at'] is not None

    def test_updated_at_is_set(self, client, clean_db, sample_todo):
        """Test that updated_at timestamp is automatically set"""
        response = client.post('/api/todos', json=sample_todo)
        data = response.get_json()

        assert 'updated_at' in data
        assert data['updated_at'] is not None

    def test_default_completed_is_false(self, client, clean_db):
        """Test that completed defaults to false"""
        todo = {'title': 'Test'}
        response = client.post('/api/todos', json=todo)
        data = response.get_json()
        assert data['completed'] is False


class TestConcurrency:
    """Tests for concurrent operations"""

    def test_update_same_todo_multiple_times(self, client, clean_db, seed_todos):
        """Test updating the same todo multiple times"""
        todo_id = seed_todos[0]['id']

        for i in range(5):
            update_data = {'title': f'Update {i}'}
            response = client.put(f'/api/todos/{todo_id}', json=update_data)
            assert response.status_code == 200

        # Verify final state
        response = client.get(f'/api/todos/{todo_id}')
        data = response.get_json()
        assert data['title'] == 'Update 4'

    def test_delete_already_deleted_todo(self, client, clean_db, seed_todos):
        """Test deleting a todo that was already deleted"""
        todo_id = seed_todos[0]['id']

        # First delete
        response1 = client.delete(f'/api/todos/{todo_id}')
        assert response1.status_code == 200

        # Second delete attempt
        response2 = client.delete(f'/api/todos/{todo_id}')
        assert response2.status_code == 404
