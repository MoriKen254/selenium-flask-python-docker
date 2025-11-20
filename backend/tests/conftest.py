"""Test configuration and fixtures for Todo API tests."""

import pytest
from typing import Generator, Any
import os
import tempfile
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from todo_api.app import create_app


@pytest.fixture
def app():
    """Create application for the tests."""
    # Create a temporary database for testing
    test_db_name = f"test_tododb_{os.getpid()}"
    test_config = {
        'TESTING': True,
        'DATABASE_URL': f'postgresql://todouser:todopass@postgres:5432/{test_db_name}'
    }
    
    # Create test database
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
        # If we can't create a test database, use an in-memory SQLite or skip database tests
        test_config['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app(test_config)
    
    with app.app_context():
        yield app
    
    # Cleanup: Drop test database
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
