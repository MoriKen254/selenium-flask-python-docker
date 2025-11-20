"""Test configuration and fixtures for Todo API tests."""

import pytest
from typing import Generator, Any, List, Dict
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from todo_api.app import create_app


@pytest.fixture
def app():
    """Create application for the tests."""
    test_config = {
        'TESTING': True,
        'DATABASE_URL': os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
    }
    
    # Try to create PostgreSQL test database if available
    if 'postgresql' in test_config['DATABASE_URL']:
        test_db_name = f"test_tododb_{os.getpid()}"
        test_config['DATABASE_URL'] = f'postgresql://todouser:todopass@postgres:5432/{test_db_name}'
        
        try:
            conn = psycopg2.connect(
                host='postgres',
                database='postgres',
                user='todouser',
                password='todopass'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f'CREATE DATABASE "{test_db_name}"')
            cur.close()
            conn.close()
            
            # Create tables in test database
            conn = psycopg2.connect(test_config['DATABASE_URL'])
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception:
            # Fallback to SQLite if PostgreSQL is not available
            test_config['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app(test_config)
    
    with app.app_context():
        yield app
    
    # Cleanup: Drop test database if PostgreSQL was used
    if 'postgresql' in test_config['DATABASE_URL']:
        try:
            conn = psycopg2.connect(
                host='postgres',
                database='postgres',
                user='todouser',
                password='todopass'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
            cur.close()
            conn.close()
        except Exception:
            pass  # Cleanup failed, but that's ok for tests


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def clean_db(app, client):
    """Clean database fixture that ensures a fresh database state for each test."""
    # Clean up any existing todos
    try:
        client.get('/api/todos')  # This will ensure database connection is established
        # Get all todos and delete them
        response = client.get('/api/todos')
        if response.status_code == 200:
            todos = response.get_json()
            for todo in todos:
                client.delete(f'/api/todos/{todo["id"]}')
    except Exception:
        pass  # If cleanup fails, continue with test
    
    yield
    
    # Post-test cleanup
    try:
        response = client.get('/api/todos')
        if response.status_code == 200:
            todos = response.get_json()
            for todo in todos:
                client.delete(f'/api/todos/{todo["id"]}')
    except Exception:
        pass


@pytest.fixture
def sample_todo():
    """Sample todo data for testing."""
    return {
        'title': 'Test Todo',
        'description': 'This is a test todo item',
        'completed': False
    }


@pytest.fixture
def seed_todos(app, client, clean_db) -> List[Dict]:
    """Create seed data for tests that need existing todos."""
    todos_data = [
        {
            'title': 'First Todo',
            'description': 'First test todo',
            'completed': False
        },
        {
            'title': 'Second Todo', 
            'description': 'Second test todo',
            'completed': True
        },
        {
            'title': 'Third Todo',
            'description': 'Third test todo',
            'completed': False
        }
    ]
    
    created_todos = []
    for todo_data in todos_data:
        response = client.post('/api/todos', json=todo_data)
        if response.status_code == 201:
            created_todos.append(response.get_json())
    
    return created_todos
