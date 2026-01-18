# Test Suite - Python Codebase Reviewer

Comprehensive test suite for all components of the Python Codebase Reviewer.

---

## Overview

The test suite covers:

1. **GitHub API Tools** (`test_github_tools.py`) - Unit tests for GitHub API integration
2. **GitHub CLI Scripts** (`test_github_cli.py`) - Tests for CLI review scripts
3. **GitHub App** (`test_github_app.py`) - Tests for webhook handler
4. **Agent Evaluations** (`../python_codebase_reviewer/eval/`) - Agent quality tests

**Total Tests**: 100+ test cases
**Coverage Target**: 80%+

---

## Quick Start

### Install Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=python_codebase_reviewer --cov-report=html

# Run specific test file
pytest tests/test_github_tools.py

# Run specific test
pytest tests/test_github_tools.py::test_fetch_pr_files_success
```

---

## Test Organization

### Unit Tests (`tests/`)

**Fast, isolated tests with mocked dependencies:**

- `test_github_tools.py` (35 tests)
  - GitHub API function tests
  - Error handling
  - Rate limiting
  - Authentication

- `test_github_cli.py` (25 tests)
  - CLI script functionality
  - gh command integration
  - File review logic
  - Output formatting

- `test_github_app.py` (30 tests)
  - Webhook signature verification
  - JWT token generation
  - Installation token retrieval
  - Webhook event handling
  - Flask app endpoints

### Integration Tests

**Tests that combine multiple components:**

- Located in same files, marked with `@pytest.mark.integration`
- Test complete workflows (fetch → review → post)
- Use mocked external APIs

### Evaluation Tests (`python_codebase_reviewer/eval/`)

**Agent quality and accuracy tests:**

- 63 test cases across 6 datasets
- Tests for security, architecture, code quality, performance
- Precision, recall, F1 score metrics

---

## Running Tests

### By Category

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# End-to-end tests
pytest -m e2e

# All except slow tests
pytest -m "not slow"
```

### By Component

```bash
# GitHub tools
pytest tests/test_github_tools.py -v

# GitHub CLI
pytest tests/test_github_cli.py -v

# GitHub App
pytest tests/test_github_app.py -v

# Evaluations
pytest python_codebase_reviewer/eval/test_eval.py -v
```

### With Coverage

```bash
# Generate coverage report
pytest --cov=python_codebase_reviewer --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Parallel Execution

```bash
# Install plugin
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### Verbose Output

```bash
# Show all test names and results
pytest -v

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Combination
pytest -vsl
```

---

## Test Markers

Tests are marked for easy filtering:

```python
@pytest.mark.unit
def test_something():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_workflow():
    """Integration test."""
    pass

@pytest.mark.requires_github
def test_with_github_api():
    """Requires GitHub token."""
    pass
```

**Available markers:**
- `unit` - Unit tests (fast, no external dependencies)
- `integration` - Integration tests (multiple components)
- `e2e` - End-to-end tests (full workflows)
- `slow` - Tests that take >5 seconds
- `requires_github` - Needs GitHub API access
- `requires_google` - Needs Google AI API access
- `requires_cli` - Needs gh CLI installed

**Usage:**
```bash
pytest -m unit  # Run only unit tests
pytest -m "not slow"  # Skip slow tests
pytest -m "requires_github"  # Only tests needing GitHub
```

---

## Test Structure

### Example Test

```python
import pytest
from unittest.mock import patch, MagicMock

def test_fetch_pr_files_success(mock_github_token, sample_pr_files):
    """
    Test successful fetching of PR files.

    Verifies:
    - Correct API endpoint called
    - Proper authentication header
    - Response parsed correctly
    - Returns expected data structure
    """
    with patch('requests.get') as mock_get:
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_pr_files
        mock_get.return_value = mock_response

        # Act
        result = fetch_pr_files('owner/repo', 123)

        # Assert
        assert len(result) == 2
        assert result[0]['filename'] == 'src/main.py'
        mock_get.assert_called_once()
```

### Test Naming Convention

- Test files: `test_<module>.py`
- Test functions: `test_<function_name>_<scenario>`
- Test classes: `Test<ClassName>`

**Examples:**
- `test_fetch_pr_files_success`
- `test_fetch_pr_files_not_found`
- `test_fetch_pr_files_unauthorized`

---

## Fixtures

### Built-in Fixtures

Located in test files:

```python
@pytest.fixture
def mock_github_token():
    """Set GITHUB_TOKEN for tests."""
    os.environ['GITHUB_TOKEN'] = 'test_token'
    yield 'test_token'
    del os.environ['GITHUB_TOKEN']

@pytest.fixture
def sample_pr_files():
    """Sample PR files response."""
    return [
        {
            'filename': 'src/main.py',
            'status': 'modified',
            'additions': 10,
            'deletions': 5
        }
    ]
```

### Using Fixtures

```python
def test_something(mock_github_token, sample_pr_files):
    # Fixtures automatically injected
    # mock_github_token sets environment variable
    # sample_pr_files provides test data
    pass
```

---

## Mocking

### Mock External APIs

```python
from unittest.mock import patch, MagicMock

def test_api_call():
    with patch('requests.get') as mock_get:
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response

        # Call function that uses requests.get
        result = my_function()

        # Verify
        mock_get.assert_called_once()
        assert result['data'] == 'test'
```

### Mock Environment Variables

```python
import os
from unittest.mock import patch

def test_with_env():
    with patch.dict(os.environ, {'MY_VAR': 'test_value'}):
        # MY_VAR is set only within this block
        result = function_using_my_var()
        assert result == 'test_value'
```

### Mock File System

```python
from unittest.mock import mock_open, patch

def test_file_read():
    mock_data = "file content"

    with patch('builtins.open', mock_open(read_data=mock_data)):
        result = read_file('test.txt')
        assert result == mock_data
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-mock

      - name: Run tests
        run: |
          pytest --cov=python_codebase_reviewer --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest
      language: system
      pass_filenames: false
      always_run: true
```

---

## Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=python_codebase_reviewer --cov-report=term-missing

# HTML report
pytest --cov=python_codebase_reviewer --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=python_codebase_reviewer --cov-report=xml
```

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| GitHub Tools | 90% | TBD |
| GitHub CLI | 80% | TBD |
| GitHub App | 85% | TBD |
| Agents | 70% | TBD |
| **Overall** | **80%** | **TBD** |

---

## Troubleshooting

### Tests Fail with Import Errors

**Solution**: Install the package in development mode
```bash
pip install -e .
```

### Tests Can't Find Modules

**Solution**: Check PYTHONPATH
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Mock Not Working

**Solution**: Ensure you're patching the right import path
```python
# If module imports like: from requests import get
patch('my_module.get')  # NOT patch('requests.get')
```

### Fixture Not Found

**Solution**: Make sure fixture is in same file or conftest.py
```python
# Option 1: Same file
@pytest.fixture
def my_fixture():
    return "value"

# Option 2: conftest.py (available to all tests)
# Create tests/conftest.py
```

### Tests Timeout

**Solution**: Use pytest-timeout
```bash
pip install pytest-timeout

# Run with timeout
pytest --timeout=300
```

---

## Best Practices

### 1. Test One Thing

```python
# Good
def test_fetch_pr_files_returns_correct_structure():
    result = fetch_pr_files('owner/repo', 123)
    assert isinstance(result, list)
    assert all('filename' in f for f in result)

# Bad
def test_everything():
    # Tests multiple unrelated things
    pass
```

### 2. Use Descriptive Names

```python
# Good
def test_fetch_pr_files_raises_error_when_pr_not_found():
    pass

# Bad
def test_error():
    pass
```

### 3. Arrange-Act-Assert

```python
def test_something():
    # Arrange - Set up test data
    data = {'key': 'value'}

    # Act - Call the function
    result = process(data)

    # Assert - Verify result
    assert result == expected
```

### 4. Don't Test Implementation Details

```python
# Good - Test behavior
def test_user_can_login():
    user = login('username', 'password')
    assert user.is_authenticated

# Bad - Test implementation
def test_login_calls_database():
    # Testing internal implementation
    pass
```

### 5. Use Fixtures for Reusable Setup

```python
@pytest.fixture
def user():
    return User(username='test')

def test_user_name(user):
    assert user.username == 'test'

def test_user_methods(user):
    assert user.is_valid()
```

---

## Writing New Tests

### 1. Identify What to Test

- **Functions**: Each function needs tests for:
  - Normal/happy path
  - Edge cases
  - Error conditions

- **Classes**: Test each method and interactions

- **Integration**: Test component interactions

### 2. Create Test File

```bash
# Create test file matching module name
touch tests/test_new_module.py
```

### 3. Write Tests

```python
import pytest
from my_module import my_function

def test_my_function_success():
    """Test successful execution."""
    result = my_function('input')
    assert result == 'expected'

def test_my_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        my_function('invalid')
```

### 4. Run Tests

```bash
pytest tests/test_new_module.py -v
```

---

## Test Data

### Sample Test Data

Located in `tests/fixtures/`:

- `sample_pr.json` - Sample PR data
- `sample_code.py` - Sample Python code for review
- `sample_review.md` - Sample review output

**Usage:**
```python
import json
from pathlib import Path

def load_fixture(name):
    path = Path(__file__).parent / 'fixtures' / name
    return json.loads(path.read_text())

def test_with_fixture():
    pr_data = load_fixture('sample_pr.json')
    # Use pr_data in test
```

---

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Mocking Guide**: https://docs.python.org/3/library/unittest.mock.html
- **Coverage.py**: https://coverage.readthedocs.io/
- **Testing Best Practices**: https://docs.pytest.org/en/latest/goodpractices.html

---

## Contributing Tests

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests pass: `pytest tests/`
3. Check coverage: `pytest --cov`
4. Add test markers if needed
5. Update this README if adding new test categories

**Target**: All PRs should maintain or improve test coverage.

---

## Quick Reference

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_github_tools.py

# Run specific test
pytest tests/test_github_tools.py::test_fetch_pr_files_success

# Run with coverage
pytest --cov=python_codebase_reviewer

# Run marked tests
pytest -m unit
pytest -m "not slow"

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Parallel execution
pytest -n auto
```

---

**Questions?** See the pytest documentation or open an issue!
