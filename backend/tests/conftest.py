import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

# Test database configuration
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql://todouser:todopass@postgres:5432/tododb_test')


@pytest.fixture(scope='session')
def test_db():
    """Create a test database for the entire test session"""
    # Parse the database URL
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', TEST_DATABASE_URL)
    if match:
        user, password, host, port, dbname = match.groups()

        # Connect to default postgres database to create test database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='tododb'  # Connect to main database
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Drop test database if exists and create new one
        try:
            cur.execute(f"DROP DATABASE IF EXISTS {dbname}")
            cur.execute(f"CREATE DATABASE {dbname}")
        except Exception as e:
            print(f"Database creation skipped or failed: {e}")
        finally:
            cur.close()
            conn.close()

        # Connect to test database and create schema
        test_conn = psycopg2.connect(TEST_DATABASE_URL)
        test_cur = test_conn.cursor()

        # Create todos table
        test_cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create trigger function
        test_cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)

        # Create trigger
        test_cur.execute("""
            DROP TRIGGER IF EXISTS update_todos_updated_at ON todos;
            CREATE TRIGGER update_todos_updated_at
                BEFORE UPDATE ON todos
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)

        test_conn.commit()
        test_cur.close()
        test_conn.close()

        yield TEST_DATABASE_URL

        # Cleanup after all tests
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='tododb'
        )
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute(f"DROP DATABASE IF EXISTS {dbname}")
        except Exception as e:
            print(f"Test database cleanup failed: {e}")
        finally:
            cur.close()
            conn.close()


@pytest.fixture(scope='function')
def db_connection(test_db):
    """Provide a database connection for each test"""
    conn = psycopg2.connect(test_db, cursor_factory=RealDictCursor)
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture(scope='function')
def clean_db(db_connection):
    """Clean the database before each test"""
    cur = db_connection.cursor()
    cur.execute("DELETE FROM todos")
    db_connection.commit()
    cur.close()
    yield db_connection


@pytest.fixture
def app(monkeypatch, test_db):
    """Create and configure a test Flask application instance"""
    # Set the test database URL
    monkeypatch.setenv('DATABASE_URL', test_db)

    # Monkey patch the DATABASE_URL in the app module
    import app as app_module
    monkeypatch.setattr(app_module, 'DATABASE_URL', test_db)

    flask_app.config['TESTING'] = True
    flask_app.config['DATABASE_URL'] = test_db

    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture
def sample_todo():
    """Sample todo data for testing"""
    return {
        'title': 'Test Todo',
        'description': 'This is a test todo',
        'completed': False
    }


@pytest.fixture
def sample_todos():
    """Sample multiple todos for testing"""
    return [
        {'title': 'Todo 1', 'description': 'First todo', 'completed': False},
        {'title': 'Todo 2', 'description': 'Second todo', 'completed': True},
        {'title': 'Todo 3', 'description': 'Third todo', 'completed': False}
    ]


@pytest.fixture
def create_todo(client):
    """Helper fixture to create a todo via API"""
    def _create_todo(data):
        response = client.post('/api/todos', json=data)
        return response
    return _create_todo


@pytest.fixture
def seed_todos(client, sample_todos):
    """Seed the database with sample todos"""
    created_todos = []
    for todo_data in sample_todos:
        response = client.post('/api/todos', json=todo_data)
        if response.status_code == 201:
            created_todos.append(response.get_json())
    return created_todos
