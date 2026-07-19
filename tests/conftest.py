"""Shared pytest fixtures for PharmFoldMDK.

Keel scaffolding (D-007): a dependency-free in-memory SQLite fixture that
proves the test-DB pattern from D-005. It uses the stdlib ``sqlite3`` module so
the suite stays green with only ``pytest`` installed; it will graduate to
SQLAlchemy / SQLModel sessions once database models exist. No application code
is imported here yet — see docs/README.md.
"""

import sqlite3

import pytest


@pytest.fixture
def sqlite_conn():
    """A fresh in-memory SQLite database, isolated per test."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
