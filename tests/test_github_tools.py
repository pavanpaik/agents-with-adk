"""
Unit tests for GitHub API tools.

Tests all functions in python_codebase_reviewer/tools/github_tools.py
using mocked HTTP responses to avoid actual API calls.

Run:
    pytest tests/test_github_tools.py -v
    pytest tests/test_github_tools.py::test_fetch_pr_files -v
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import json

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python_codebase_reviewer.tools.github_tools import (
    fetch_pr_files,
    fetch_file_content,
    fetch_pr_info,
    fetch_issue_comments,
    post_pr_review,
    post_pr_line_comment,
    GitHubAPIError
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_github_token():
    """Temporarily set GITHUB_TOKEN for tests."""
    original = os.environ.get('GITHUB_TOKEN')
    os.environ['GITHUB_TOKEN'] = 'test_token_12345'
    yield 'test_token_12345'
    if original:
        os.environ['GITHUB_TOKEN'] = original
    else:
        del os.environ['GITHUB_TOKEN']


@pytest.fixture
def sample_pr_files():
    """Sample PR files response from GitHub API."""
    return [
        {
            'sha': 'abc123',
            'filename': 'src/main.py',
            'status': 'modified',
            'additions': 10,
            'deletions': 5,
            'changes': 15,
            'blob_url': 'https://github.com/owner/repo/blob/abc123/src/main.py',
            'raw_url': 'https://raw.githubusercontent.com/owner/repo/abc123/src/main.py',
            'patch': '@@ -1,5 +1,10 @@\n+def new_function():\n+    pass'
        },
        {
            'sha': 'def456',
            'filename': 'tests/test_main.py',
            'status': 'added',
            'additions': 20,
            'deletions': 0,
            'changes': 20,
            'blob_url': 'https://github.com/owner/repo/blob/def456/tests/test_main.py',
            'raw_url': 'https://raw.githubusercontent.com/owner/repo/def456/tests/test_main.py'
        }
    ]


@pytest.fixture
def sample_pr_info():
    """Sample PR info response from GitHub API."""
    return {
        'number': 123,
        'title': 'Add new feature',
        'body': 'This PR adds a new feature',
        'state': 'open',
        'user': {
            'login': 'contributor',
            'id': 12345
        },
        'head': {
            'ref': 'feature-branch',
            'sha': 'abc123'
        },
        'base': {
            'ref': 'main',
            'sha': 'def456'
        },
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-02T00:00:00Z'
    }


@pytest.fixture
def sample_file_content():
    """Sample file content."""
    return """def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""


@pytest.fixture
def sample_comments():
    """Sample issue comments response."""
    return [
        {
            'id': 1,
            'user': {'login': 'reviewer1'},
            'body': 'LGTM!',
            'created_at': '2024-01-01T00:00:00Z'
        },
        {
            'id': 2,
            'user': {'login': 'reviewer2'},
            'body': 'Please fix the typo',
            'created_at': '2024-01-02T00:00:00Z'
        }
    ]


# ============================================================================
# Tests for fetch_pr_files
# ============================================================================

def test_fetch_pr_files_success(mock_github_token, sample_pr_files):
    """Test successful fetching of PR files."""
    with patch('requests.get') as mock_get:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_pr_files
        mock_get.return_value = mock_response

        # Call function
        result = fetch_pr_files('owner/repo', 123)

        # Verify
        assert len(result) == 2
        assert result[0]['filename'] == 'src/main.py'
        assert result[0]['status'] == 'modified'
        assert result[1]['filename'] == 'tests/test_main.py'
        assert result[1]['status'] == 'added'

        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'owner/repo' in call_args[0][0]
        assert '123' in call_args[0][0]
        assert call_args[1]['headers']['Authorization'] == 'token test_token_12345'


def test_fetch_pr_files_not_found(mock_github_token):
    """Test 404 error when PR not found."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_get.return_value = mock_response

        with pytest.raises(GitHubAPIError) as exc_info:
            fetch_pr_files('owner/repo', 999)

        assert '404' in str(exc_info.value)


def test_fetch_pr_files_unauthorized(mock_github_token):
    """Test 401 error with invalid token."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Bad credentials'
        mock_get.return_value = mock_response

        with pytest.raises(GitHubAPIError) as exc_info:
            fetch_pr_files('owner/repo', 123)

        assert '401' in str(exc_info.value)


def test_fetch_pr_files_no_token():
    """Test error when GITHUB_TOKEN not set."""
    # Ensure token is not set
    original = os.environ.pop('GITHUB_TOKEN', None)

    try:
        with pytest.raises(GitHubAPIError) as exc_info:
            fetch_pr_files('owner/repo', 123)

        assert 'GITHUB_TOKEN' in str(exc_info.value)

    finally:
        if original:
            os.environ['GITHUB_TOKEN'] = original


# ============================================================================
# Tests for fetch_file_content
# ============================================================================

def test_fetch_file_content_success(mock_github_token, sample_file_content):
    """Test successful fetching of file content."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_file_content
        mock_get.return_value = mock_response

        result = fetch_file_content('owner/repo', 'src/main.py', 'main')

        assert result == sample_file_content
        assert 'def hello_world' in result

        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'raw.githubusercontent.com' in call_args[0][0]
        assert 'owner/repo' in call_args[0][0]
        assert 'main/src/main.py' in call_args[0][0]


def test_fetch_file_content_custom_ref(mock_github_token, sample_file_content):
    """Test fetching file content from custom ref (branch)."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_file_content
        mock_get.return_value = mock_response

        result = fetch_file_content('owner/repo', 'src/main.py', 'feature-branch')

        assert result == sample_file_content

        # Verify correct ref in URL
        call_args = mock_get.call_args
        assert 'feature-branch/src/main.py' in call_args[0][0]


def test_fetch_file_content_not_found(mock_github_token):
    """Test 404 error when file not found."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(GitHubAPIError) as exc_info:
            fetch_file_content('owner/repo', 'nonexistent.py')

        assert '404' in str(exc_info.value)


# ============================================================================
# Tests for fetch_pr_info
# ============================================================================

def test_fetch_pr_info_success(mock_github_token, sample_pr_info):
    """Test successful fetching of PR info."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_pr_info
        mock_get.return_value = mock_response

        result = fetch_pr_info('owner/repo', 123)

        assert result['number'] == 123
        assert result['title'] == 'Add new feature'
        assert result['state'] == 'open'
        assert result['user']['login'] == 'contributor'
        assert result['head']['ref'] == 'feature-branch'


def test_fetch_pr_info_closed_pr(mock_github_token, sample_pr_info):
    """Test fetching info for closed PR."""
    with patch('requests.get') as mock_get:
        closed_pr = sample_pr_info.copy()
        closed_pr['state'] = 'closed'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = closed_pr
        mock_get.return_value = mock_response

        result = fetch_pr_info('owner/repo', 123)

        assert result['state'] == 'closed'


# ============================================================================
# Tests for fetch_issue_comments
# ============================================================================

def test_fetch_issue_comments_success(mock_github_token, sample_comments):
    """Test successful fetching of issue comments."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_comments
        mock_get.return_value = mock_response

        result = fetch_issue_comments('owner/repo', 123)

        assert len(result) == 2
        assert result[0]['user']['login'] == 'reviewer1'
        assert result[0]['body'] == 'LGTM!'
        assert result[1]['user']['login'] == 'reviewer2'


def test_fetch_issue_comments_empty(mock_github_token):
    """Test fetching comments when there are none."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = fetch_issue_comments('owner/repo', 123)

        assert result == []


# ============================================================================
# Tests for post_pr_review
# ============================================================================

def test_post_pr_review_success(mock_github_token):
    """Test successful posting of PR review."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 12345}
        mock_post.return_value = mock_response

        result = post_pr_review(
            'owner/repo',
            123,
            'Great work!',
            event='COMMENT'
        )

        assert result['id'] == 12345

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'owner/repo' in call_args[0][0]
        assert '123' in call_args[0][0]

        # Verify body
        body = call_args[1]['json']
        assert body['body'] == 'Great work!'
        assert body['event'] == 'COMMENT'


def test_post_pr_review_approve(mock_github_token):
    """Test posting approval review."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 12345}
        mock_post.return_value = mock_response

        result = post_pr_review(
            'owner/repo',
            123,
            'LGTM!',
            event='APPROVE'
        )

        # Verify event type
        call_args = mock_post.call_args
        body = call_args[1]['json']
        assert body['event'] == 'APPROVE'


def test_post_pr_review_request_changes(mock_github_token):
    """Test requesting changes."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 12345}
        mock_post.return_value = mock_response

        result = post_pr_review(
            'owner/repo',
            123,
            'Please fix security issues',
            event='REQUEST_CHANGES'
        )

        call_args = mock_post.call_args
        body = call_args[1]['json']
        assert body['event'] == 'REQUEST_CHANGES'


def test_post_pr_review_with_comments(mock_github_token):
    """Test posting review with line comments."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 12345}
        mock_post.return_value = mock_response

        comments = [
            {
                'path': 'src/main.py',
                'line': 42,
                'body': 'This could cause SQL injection'
            }
        ]

        result = post_pr_review(
            'owner/repo',
            123,
            'Found security issues',
            event='REQUEST_CHANGES',
            comments=comments
        )

        call_args = mock_post.call_args
        body = call_args[1]['json']
        assert 'comments' in body
        assert len(body['comments']) == 1
        assert body['comments'][0]['path'] == 'src/main.py'


def test_post_pr_review_forbidden(mock_github_token):
    """Test 403 error when lacking permissions."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = 'Forbidden'
        mock_post.return_value = mock_response

        with pytest.raises(GitHubAPIError) as exc_info:
            post_pr_review('owner/repo', 123, 'Review')

        assert '403' in str(exc_info.value)


# ============================================================================
# Tests for post_pr_line_comment
# ============================================================================

def test_post_pr_line_comment_success(mock_github_token):
    """Test successful posting of line comment."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 67890}
        mock_post.return_value = mock_response

        result = post_pr_line_comment(
            'owner/repo',
            123,
            'Use parameterized queries here',
            'abc123',
            'src/db.py',
            42
        )

        assert result['id'] == 67890

        # Verify API call
        call_args = mock_post.call_args
        body = call_args[1]['json']
        assert body['body'] == 'Use parameterized queries here'
        assert body['commit_id'] == 'abc123'
        assert body['path'] == 'src/db.py'
        assert body['line'] == 42


# ============================================================================
# Integration Tests (Multiple API Calls)
# ============================================================================

def test_review_workflow_integration(mock_github_token, sample_pr_files, sample_file_content):
    """Test complete review workflow: fetch files -> fetch content -> post review."""
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        # Mock fetch_pr_files
        files_response = MagicMock()
        files_response.status_code = 200
        files_response.json.return_value = sample_pr_files

        # Mock fetch_file_content
        content_response = MagicMock()
        content_response.status_code = 200
        content_response.text = sample_file_content

        mock_get.side_effect = [files_response, content_response]

        # Mock post_pr_review
        post_response = MagicMock()
        post_response.status_code = 200
        post_response.json.return_value = {'id': 99999}
        mock_post.return_value = post_response

        # Simulate workflow
        files = fetch_pr_files('owner/repo', 123)
        assert len(files) == 2

        content = fetch_file_content('owner/repo', files[0]['filename'])
        assert 'def hello_world' in content

        review = post_pr_review('owner/repo', 123, 'Review complete')
        assert review['id'] == 99999

        # Verify all API calls were made
        assert mock_get.call_count == 2
        assert mock_post.call_count == 1


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_rate_limit_error(mock_github_token):
    """Test handling of rate limit errors."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = 'API rate limit exceeded'
        mock_response.headers = {'X-RateLimit-Remaining': '0'}
        mock_get.return_value = mock_response

        with pytest.raises(GitHubAPIError) as exc_info:
            fetch_pr_files('owner/repo', 123)

        assert 'rate limit' in str(exc_info.value).lower()


def test_network_timeout():
    """Test handling of network timeouts."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception('Connection timeout')

        with pytest.raises(GitHubAPIError):
            fetch_pr_files('owner/repo', 123)


def test_invalid_json_response(mock_github_token):
    """Test handling of invalid JSON in response."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_get.return_value = mock_response

        with pytest.raises(GitHubAPIError):
            fetch_pr_files('owner/repo', 123)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
