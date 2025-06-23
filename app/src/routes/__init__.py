"""
This module contains route handlers for the application.
"""
from .main import main
from .restock import restock
from .history import history
from .auth import auth
from .statistics import statistics

__all__ = ['main', 'restock', 'history', 'auth', 'statistics']
