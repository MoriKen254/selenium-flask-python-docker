"""Todo API - A modern Flask REST API for Todo List management.

This package provides a RESTful API for managing todo items with full CRUD operations.
The API uses PostgreSQL for data persistence and supports CORS for frontend integration.
"""

__version__ = "1.0.0"
__author__ = "Todo API Team"
__email__ = "dev@todo-api.com"

from .app import create_app

__all__ = ["create_app", "__version__"]
