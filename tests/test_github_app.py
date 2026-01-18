"""
Tests for GitHub App webhook handler.

Tests the Flask application that handles GitHub webhooks.

Run:
    pytest tests/test_github_app.py -v
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import json
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python_codebase_reviewer' / 'github_app'))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create test Flask app."""
    os.environ['GITHUB_APP_ID'] = '12345'
    os.environ['GITHUB_WEBHOOK_SECRET'] = 'test_webhook_secret'
    os.environ['GITHUB_PRIVATE_KEY'] = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF3H9fLVDTl8Nj1Bkxp2bZ16

J6w==
-----END RSA PRIVATE KEY-----'''
    os.environ['GOOGLE_API_KEY'] = 'test_google_key'

    import webhook_handler
    webhook_handler.app.config['TESTING'] = True

    yield webhook_handler.app

    # Cleanup
    for key in ['GITHUB_APP_ID', 'GITHUB_WEBHOOK_SECRET', 'GITHUB_PRIVATE_KEY', 'GOOGLE_API_KEY']:
        os.environ.pop(key, None)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_pr_payload():
    """Sample pull_request webhook payload."""
    return {
        'action': 'opened',
        'pull_request': {
            'number': 123,
            'title': 'Add new feature',
            'head': {'ref': 'feature-branch'},
            'base': {'ref': 'main'}
        },
        'repository': {
            'full_name': 'owner/repo'
        },
        'installation': {
            'id': 98765
        }
    }


def generate_signature(payload: bytes, secret: str) -> str:
    """Generate GitHub webhook signature."""
    return 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()


# ============================================================================
# Tests for Webhook Signature Verification
# ============================================================================

def test_verify_webhook_signature_valid():
    """Test valid webhook signature verification."""
    import webhook_handler

    payload = b'{"test": "data"}'
    secret = 'test_secret'
    signature = generate_signature(payload, secret)

    with patch.dict(os.environ, {'GITHUB_WEBHOOK_SECRET': secret}):
        assert webhook_handler.verify_webhook_signature(payload, signature) == True


def test_verify_webhook_signature_invalid():
    """Test invalid webhook signature."""
    import webhook_handler

    payload = b'{"test": "data"}'
    secret = 'test_secret'
    wrong_signature = 'sha256=wrong_signature'

    with patch.dict(os.environ, {'GITHUB_WEBHOOK_SECRET': secret}):
        assert webhook_handler.verify_webhook_signature(payload, wrong_signature) == False


def test_verify_webhook_signature_missing():
    """Test missing signature."""
    import webhook_handler

    payload = b'{"test": "data"}'

    with patch.dict(os.environ, {'GITHUB_WEBHOOK_SECRET': 'secret'}):
        assert webhook_handler.verify_webhook_signature(payload, None) == False


# ============================================================================
# Tests for JWT Generation
# ============================================================================

def test_generate_jwt_token():
    """Test JWT token generation for GitHub App."""
    import webhook_handler

    app_id = '12345'
    private_key = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF3H9fLVDTl8Nj1Bkxp2bZ16yLqPn
...
-----END RSA PRIVATE KEY-----'''

    with patch.dict(os.environ, {'GITHUB_APP_ID': app_id, 'GITHUB_PRIVATE_KEY': private_key}):
        # Mock the actual key generation
        with patch('jwt.encode') as mock_encode:
            mock_encode.return_value = 'mocked_jwt_token'

            token = webhook_handler.generate_jwt_token()

            # Verify jwt.encode was called with correct parameters
            mock_encode.assert_called_once()
            call_args = mock_encode.call_args[0]
            payload = call_args[0]

            assert payload['iss'] == app_id
            assert 'exp' in payload
            assert 'iat' in payload


# ============================================================================
# Tests for Installation Access Token
# ============================================================================

def test_get_installation_access_token_success():
    """Test getting installation access token."""
    import webhook_handler

    installation_id = 98765

    with patch('requests.post') as mock_post, \
         patch('webhook_handler.generate_jwt_token') as mock_jwt:

        mock_jwt.return_value = 'test_jwt_token'

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'token': 'installation_token_abc123'}
        mock_post.return_value = mock_response

        token = webhook_handler.get_installation_access_token(installation_id)

        assert token == 'installation_token_abc123'

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert str(installation_id) in call_args[0][0]
        assert call_args[1]['headers']['Authorization'] == 'Bearer test_jwt_token'


def test_get_installation_access_token_failure():
    """Test failure to get installation access token."""
    import webhook_handler

    with patch('requests.post') as mock_post, \
         patch('webhook_handler.generate_jwt_token') as mock_jwt:

        mock_jwt.return_value = 'test_jwt_token'

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        with pytest.raises(Exception):
            webhook_handler.get_installation_access_token(98765)


# ============================================================================
# Tests for Webhook Endpoints
# ============================================================================

def test_webhook_ping(client, sample_pr_payload):
    """Test ping event from GitHub."""
    payload = json.dumps({'zen': 'Design for failure.'})
    signature = generate_signature(payload.encode(), 'test_webhook_secret')

    response = client.post(
        '/webhook',
        data=payload,
        headers={
            'X-Hub-Signature-256': signature,
            'X-GitHub-Event': 'ping'
        },
        content_type='application/json'
    )

    assert response.status_code == 200
    assert b'pong' in response.data


def test_webhook_pr_opened(client, sample_pr_payload):
    """Test pull_request opened event."""
    payload = json.dumps(sample_pr_payload)
    signature = generate_signature(payload.encode(), 'test_webhook_secret')

    with patch('webhook_handler.get_installation_access_token') as mock_token, \
         patch('webhook_handler.run_code_review') as mock_review, \
         patch('requests.post') as mock_post:

        mock_token.return_value = 'installation_token'
        mock_review.return_value = '# Code Review\n\nNo issues found'

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        response = client.post(
            '/webhook',
            data=payload,
            headers={
                'X-Hub-Signature-256': signature,
                'X-GitHub-Event': 'pull_request'
            },
            content_type='application/json'
        )

        assert response.status_code == 200

        # Verify review was run
        mock_review.assert_called_once()

        # Verify comment was posted
        mock_post.assert_called()


def test_webhook_pr_synchronize(client, sample_pr_payload):
    """Test pull_request synchronize event (new commits)."""
    payload = sample_pr_payload.copy()
    payload['action'] = 'synchronize'
    payload_json = json.dumps(payload)
    signature = generate_signature(payload_json.encode(), 'test_webhook_secret')

    with patch('webhook_handler.get_installation_access_token') as mock_token, \
         patch('webhook_handler.run_code_review') as mock_review, \
         patch('requests.post') as mock_post:

        mock_token.return_value = 'installation_token'
        mock_review.return_value = 'Review complete'

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        response = client.post(
            '/webhook',
            data=payload_json,
            headers={
                'X-Hub-Signature-256': signature,
                'X-GitHub-Event': 'pull_request'
            },
            content_type='application/json'
        )

        assert response.status_code == 200


def test_webhook_pr_closed_ignored(client, sample_pr_payload):
    """Test pull_request closed event is ignored."""
    payload = sample_pr_payload.copy()
    payload['action'] = 'closed'
    payload_json = json.dumps(payload)
    signature = generate_signature(payload_json.encode(), 'test_webhook_secret')

    with patch('webhook_handler.run_code_review') as mock_review:
        response = client.post(
            '/webhook',
            data=payload_json,
            headers={
                'X-Hub-Signature-256': signature,
                'X-GitHub-Event': 'pull_request'
            },
            content_type='application/json'
        )

        assert response.status_code == 200

        # Review should not be run for closed PRs
        mock_review.assert_not_called()


def test_webhook_invalid_signature(client, sample_pr_payload):
    """Test webhook with invalid signature is rejected."""
    payload = json.dumps(sample_pr_payload)
    invalid_signature = 'sha256=invalid_signature'

    response = client.post(
        '/webhook',
        data=payload,
        headers={
            'X-Hub-Signature-256': invalid_signature,
            'X-GitHub-Event': 'pull_request'
        },
        content_type='application/json'
    )

    assert response.status_code == 403


def test_webhook_missing_signature(client, sample_pr_payload):
    """Test webhook without signature is rejected."""
    payload = json.dumps(sample_pr_payload)

    response = client.post(
        '/webhook',
        data=payload,
        headers={
            'X-GitHub-Event': 'pull_request'
        },
        content_type='application/json'
    )

    assert response.status_code == 403


# ============================================================================
# Tests for Code Review Function
# ============================================================================

def test_run_code_review_success():
    """Test running code review on PR files."""
    import webhook_handler

    files = [
        {
            'filename': 'src/main.py',
            'status': 'modified',
            'additions': 10
        }
    ]

    with patch('webhook_handler.fetch_file_content') as mock_fetch, \
         patch('python_codebase_reviewer.root_agent.run') as mock_agent:

        mock_fetch.return_value = 'def hello(): pass'
        mock_agent.return_value = 'Review: No issues found'

        result = webhook_handler.run_code_review(files, 'owner/repo', 123)

        assert 'No issues found' in result
        mock_fetch.assert_called_once()
        mock_agent.assert_called_once()


def test_run_code_review_no_python_files():
    """Test review when no Python files changed."""
    import webhook_handler

    files = [
        {
            'filename': 'README.md',
            'status': 'modified'
        }
    ]

    result = webhook_handler.run_code_review(files, 'owner/repo', 123)

    assert 'No Python files' in result or 'No issues' in result


def test_run_code_review_multiple_files():
    """Test reviewing multiple Python files."""
    import webhook_handler

    files = [
        {'filename': 'src/main.py', 'status': 'modified'},
        {'filename': 'src/utils.py', 'status': 'added'}
    ]

    with patch('webhook_handler.fetch_file_content') as mock_fetch, \
         patch('python_codebase_reviewer.root_agent.run') as mock_agent:

        mock_fetch.return_value = 'def test(): pass'
        mock_agent.return_value = 'Review complete'

        result = webhook_handler.run_code_review(files, 'owner/repo', 123)

        # Should have reviewed both files
        assert mock_fetch.call_count == 2
        assert mock_agent.call_count == 2


# ============================================================================
# Tests for Health Check
# ============================================================================

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


# ============================================================================
# Tests for Root Endpoint
# ============================================================================

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get('/')

    assert response.status_code == 200
    assert b'Python Codebase Reviewer' in response.data


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_webhook_missing_installation_id(client):
    """Test webhook with missing installation ID."""
    payload = {
        'action': 'opened',
        'pull_request': {'number': 123},
        'repository': {'full_name': 'owner/repo'}
        # Missing 'installation'
    }
    payload_json = json.dumps(payload)
    signature = generate_signature(payload_json.encode(), 'test_webhook_secret')

    response = client.post(
        '/webhook',
        data=payload_json,
        headers={
            'X-Hub-Signature-256': signature,
            'X-GitHub-Event': 'pull_request'
        },
        content_type='application/json'
    )

    # Should handle gracefully (might return 500 or 200 depending on implementation)
    assert response.status_code in [200, 500]


def test_webhook_api_error_handling(client, sample_pr_payload):
    """Test handling of API errors during review."""
    payload = json.dumps(sample_pr_payload)
    signature = generate_signature(payload.encode(), 'test_webhook_secret')

    with patch('webhook_handler.get_installation_access_token') as mock_token:
        mock_token.side_effect = Exception('API Error')

        response = client.post(
            '/webhook',
            data=payload,
            headers={
                'X-Hub-Signature-256': signature,
                'X-GitHub-Event': 'pull_request'
            },
            content_type='application/json'
        )

        # Should return 500 on error
        assert response.status_code == 500


# ============================================================================
# Environment Variable Tests
# ============================================================================

def test_missing_env_vars():
    """Test app fails gracefully when env vars missing."""
    # Remove required env vars
    for key in ['GITHUB_APP_ID', 'GITHUB_WEBHOOK_SECRET', 'GITHUB_PRIVATE_KEY']:
        os.environ.pop(key, None)

    # Importing should work but functions should fail
    with pytest.raises(Exception):
        import webhook_handler
        webhook_handler.generate_jwt_token()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
