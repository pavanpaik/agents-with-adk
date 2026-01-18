"""
Shared pytest fixtures and configuration.

This file is automatically loaded by pytest and makes fixtures
available to all test files.
"""

import os
import pytest
from unittest.mock import MagicMock


# ============================================================================
# Environment Setup
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    Automatically set up test environment for all tests.

    Sets default values for environment variables to prevent
    tests from accidentally using real API keys or making real API calls.
    """
    # Set test environment variables (will be overridden by test-specific fixtures)
    monkeypatch.setenv('GITHUB_TOKEN', 'test_github_token_12345')
    monkeypatch.setenv('GOOGLE_API_KEY', 'test_google_api_key_12345')

    # Set test mode
    monkeypatch.setenv('TESTING', 'true')


# ============================================================================
# Common Fixtures
# ============================================================================

@pytest.fixture
def sample_python_code():
    """Sample Python code for testing reviews."""
    return """
def calculate_total(items):
    \"\"\"Calculate total price of items.\"\"\"
    total = 0
    for item in items:
        total += item.price
    return total


def get_user_by_id(user_id):
    \"\"\"Fetch user from database.\"\"\"
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()


class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def get_total(self):
        return calculate_total(self.items)
"""


@pytest.fixture
def sample_pr_data():
    """Sample pull request data structure."""
    return {
        'number': 123,
        'title': 'Add new feature',
        'body': 'This PR adds a new feature for user authentication',
        'state': 'open',
        'user': {
            'login': 'contributor',
            'id': 12345
        },
        'head': {
            'ref': 'feature-branch',
            'sha': 'abc123def456'
        },
        'base': {
            'ref': 'main',
            'sha': 'def456abc123'
        },
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-02T12:00:00Z',
        'html_url': 'https://github.com/owner/repo/pull/123'
    }


@pytest.fixture
def sample_pr_files():
    """Sample list of files changed in a PR."""
    return [
        {
            'sha': 'abc123',
            'filename': 'src/main.py',
            'status': 'modified',
            'additions': 15,
            'deletions': 3,
            'changes': 18,
            'patch': '@@ -10,3 +10,15 @@\n+def new_function():\n+    pass'
        },
        {
            'sha': 'def456',
            'filename': 'src/utils.py',
            'status': 'added',
            'additions': 25,
            'deletions': 0,
            'changes': 25
        },
        {
            'sha': 'ghi789',
            'filename': 'tests/test_main.py',
            'status': 'modified',
            'additions': 10,
            'deletions': 2,
            'changes': 12
        }
    ]


@pytest.fixture
def sample_review_output():
    """Sample review output from AI agent."""
    return """
# Code Review Results

## Security Issues

### 🔴 CRITICAL: SQL Injection Vulnerability (Line 15)

**Issue**: The function `get_user_by_id` uses string formatting to construct SQL queries, which is vulnerable to SQL injection attacks.

**Current Code**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Recommended Fix**:
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

## Code Quality

### 🟡 MEDIUM: Consider using sum() with generator expression (Line 5)

**Issue**: Manual loop for summing values when `sum()` is more Pythonic.

**Suggested Improvement**:
```python
def calculate_total(items):
    return sum(item.price for item in items)
```

## Summary

- 1 Critical issue
- 0 High issues
- 1 Medium issue
- 0 Low issues

**Action Required**: Fix critical SQL injection before merging.
"""


# ============================================================================
# Mock Helpers
# ============================================================================

def create_mock_response(status_code=200, json_data=None, text=''):
    """
    Create a mock HTTP response object.

    Args:
        status_code: HTTP status code
        json_data: Data to return from .json()
        text: Text content

    Returns:
        MagicMock response object
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.text = text

    if json_data is not None:
        mock_response.json.return_value = json_data
    else:
        mock_response.json.side_effect = ValueError('No JSON')

    return mock_response


@pytest.fixture
def mock_requests_get(monkeypatch):
    """
    Fixture to easily mock requests.get in tests.

    Usage:
        def test_something(mock_requests_get):
            mock_requests_get.return_value = create_mock_response(200, {'data': 'value'})
            # Now any requests.get() call will return this mock
    """
    mock = MagicMock()
    monkeypatch.setattr('requests.get', mock)
    return mock


@pytest.fixture
def mock_requests_post(monkeypatch):
    """
    Fixture to easily mock requests.post in tests.

    Usage:
        def test_something(mock_requests_post):
            mock_requests_post.return_value = create_mock_response(201, {'id': 123})
    """
    mock = MagicMock()
    monkeypatch.setattr('requests.post', mock)
    return mock


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (takes >5 seconds)"
    )
    config.addinivalue_line(
        "markers", "requires_github: mark test as requiring GitHub API access"
    )
    config.addinivalue_line(
        "markers", "requires_google: mark test as requiring Google AI API access"
    )
    config.addinivalue_line(
        "markers", "requires_cli: mark test as requiring gh CLI"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically based on test names.

    This adds markers based on naming conventions:
    - Tests in test_github_tools.py get 'unit' marker
    - Tests with 'integration' in name get 'integration' marker
    - Tests with 'e2e' in name get 'e2e' marker
    """
    for item in items:
        # Add unit marker to tests in test files
        if 'test_github_tools' in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        if 'test_github_cli' in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to integration tests
        if 'integration' in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Add e2e marker to end-to-end tests
        if 'e2e' in item.nodeid:
            item.add_marker(pytest.mark.e2e)


# ============================================================================
# Session Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def test_data_dir():
    """Return path to test data directory."""
    import pathlib
    return pathlib.Path(__file__).parent / 'fixtures'


# ============================================================================
# Utility Functions
# ============================================================================

def load_test_fixture(filename):
    """
    Load a test fixture file.

    Args:
        filename: Name of fixture file (e.g., 'sample_pr.json')

    Returns:
        Contents of fixture file
    """
    import json
    from pathlib import Path

    fixture_path = Path(__file__).parent / 'fixtures' / filename

    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    if filename.endswith('.json'):
        return json.loads(fixture_path.read_text())
    else:
        return fixture_path.read_text()
