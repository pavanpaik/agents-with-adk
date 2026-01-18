"""
GitHub App webhook handler for Python Codebase Reviewer.

This Flask application receives webhook events from GitHub and runs
code reviews on pull requests automatically.

Production-ready features:
- Webhook signature verification
- GitHub App authentication
- Async review processing
- Error handling and logging
- Health checks
"""
import os
import sys
import hmac
import hashlib
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List

from flask import Flask, request, jsonify
import requests
import jwt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from python_codebase_reviewer import root_agent
    from python_codebase_reviewer.tools.github_tools import (
        fetch_pr_files,
        fetch_file_content,
        fetch_pr_info,
        post_pr_comment,
        GitHubAPIError
    )
    logger.info("✅ Successfully imported Python Codebase Reviewer")
except ImportError as e:
    logger.error(f"❌ Failed to import Python Codebase Reviewer: {e}")
    logger.error("Make sure google-adk is installed: pip install google-adk")

# Initialize Flask app
app = Flask(__name__)

# Configuration from environment
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Validate required environment variables
REQUIRED_ENV_VARS = {
    'GITHUB_WEBHOOK_SECRET': GITHUB_WEBHOOK_SECRET,
    'GITHUB_APP_ID': GITHUB_APP_ID,
    'GITHUB_PRIVATE_KEY': GITHUB_PRIVATE_KEY,
    'GOOGLE_API_KEY': GOOGLE_API_KEY,
}

missing_vars = [k for k, v in REQUIRED_ENV_VARS.items() if not v]
if missing_vars:
    logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")


def verify_webhook_signature(payload_body: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature.

    Args:
        payload_body: Raw request body as bytes
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("⚠️  GITHUB_WEBHOOK_SECRET not set - signature verification disabled")
        return True

    if not signature:
        logger.warning("⚠️  No signature provided in request")
        return False

    # Compute expected signature
    expected = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison
    is_valid = hmac.compare_digest(expected, signature)

    if not is_valid:
        logger.warning(f"⚠️  Invalid webhook signature")

    return is_valid


def generate_jwt_token() -> str:
    """
    Generate JWT token for GitHub App authentication.

    Returns:
        JWT token string
    """
    now = int(time.time())

    payload = {
        'iat': now,
        'exp': now + 600,  # Token expires in 10 minutes
        'iss': GITHUB_APP_ID
    }

    # Sign with private key
    token = jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm='RS256')

    return token


def get_installation_access_token(installation_id: int) -> str:
    """
    Get installation access token for GitHub App.

    Args:
        installation_id: GitHub App installation ID

    Returns:
        Access token string

    Raises:
        Exception: If token request fails
    """
    # Generate JWT
    jwt_token = generate_jwt_token()

    # Request installation token
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'

    try:
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['token']
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to get installation token: {e}")
        raise


def fetch_pr_files_with_content(
    repo: str,
    pr_number: int,
    token: str
) -> List[Dict]:
    """
    Fetch PR files with their content.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
        token: GitHub access token

    Returns:
        List of file objects with content
    """
    # Temporarily set token for GitHub API calls
    original_token = os.getenv('GITHUB_TOKEN')
    os.environ['GITHUB_TOKEN'] = token

    try:
        files = fetch_pr_files(repo, pr_number)

        # Fetch content for each Python file
        for file in files:
            if file['filename'].endswith('.py'):
                try:
                    # Fetch content from PR branch
                    content = fetch_file_content(
                        repo,
                        file['filename'],
                        ref=f"refs/pull/{pr_number}/head"
                    )
                    file['content'] = content
                except GitHubAPIError as e:
                    logger.warning(f"⚠️  Could not fetch content for {file['filename']}: {e}")
                    file['content'] = None

        return files

    finally:
        # Restore original token
        if original_token:
            os.environ['GITHUB_TOKEN'] = original_token
        else:
            os.environ.pop('GITHUB_TOKEN', None)


def run_code_review(files: List[Dict], repo: str, pr_number: int) -> str:
    """
    Run code review on files using Python Codebase Reviewer.

    Args:
        files: List of file objects with content
        repo: Repository name
        pr_number: Pull request number

    Returns:
        Review results as markdown
    """
    logger.info(f"🔍 Reviewing {len(files)} files...")

    results = []

    for file in files:
        if not file.get('content'):
            continue

        filename = file['filename']
        content = file['content']

        logger.info(f"  📝 Reviewing {filename}...")

        # Create review request
        review_request = f"""
Review this Python file from a pull request:

**Repository**: {repo}
**PR**: #{pr_number}
**File**: `{filename}`

```python
{content}
```

Provide a comprehensive review with:
- Security vulnerabilities (OWASP Top 10)
- Architecture issues (SOLID principles)
- Code quality (PEP standards)
- Performance issues
- Python best practices

Focus on actionable findings with specific line numbers and fixes.
"""

        try:
            response = root_agent.run(review_request)
            results.append({
                'file': filename,
                'review': response,
                'status': 'success'
            })
            logger.info(f"  ✅ Completed review of {filename}")

        except Exception as e:
            logger.error(f"  ❌ Error reviewing {filename}: {e}")
            results.append({
                'file': filename,
                'review': f"Error during review: {str(e)}",
                'status': 'error'
            })

    # Format results
    return format_review_results(results, repo, pr_number)


def format_review_results(results: List[Dict], repo: str, pr_number: int) -> str:
    """
    Format review results as GitHub-flavored markdown.

    Args:
        results: List of review results
        repo: Repository name
        pr_number: Pull request number

    Returns:
        Formatted markdown string
    """
    output = []

    # Header
    output.append("# 🔍 Python Code Review Results\n\n")
    output.append(f"**Repository**: {repo}\n")
    output.append(f"**Pull Request**: #{pr_number}\n")
    output.append(f"**Reviewed by**: Python Codebase Reviewer (GitHub App)\n\n")
    output.append("---\n\n")

    # Count findings
    total_critical = sum(
        r['review'].upper().count('CRITICAL')
        for r in results if r['status'] == 'success'
    )
    total_high = sum(
        r['review'].upper().count('HIGH')
        for r in results if r['status'] == 'success'
    )
    total_medium = sum(
        r['review'].upper().count('MEDIUM')
        for r in results if r['status'] == 'success'
    )

    # Summary
    output.append("## 📊 Summary\n\n")

    if total_critical + total_high + total_medium == 0:
        output.append("✅ **No issues found!** Code looks good.\n\n")
    else:
        if total_critical > 0:
            output.append(f"- 🔴 **{total_critical} Critical** - Immediate action required\n")
        if total_high > 0:
            output.append(f"- 🟠 **{total_high} High** - Important to fix\n")
        if total_medium > 0:
            output.append(f"- 🟡 **{total_medium} Medium** - Should be addressed\n")
        output.append("\n")

        if total_critical > 0:
            output.append("> ⚠️ **Warning**: Critical security issues detected!\n\n")

    output.append("---\n\n")

    # Detailed results
    output.append("## 📁 Detailed Review\n\n")

    for result in results:
        output.append(f"### 📄 `{result['file']}`\n\n")

        if result['status'] == 'error':
            output.append(f"❌ **Error**: {result['review']}\n\n")
        else:
            # Count issues in this file
            critical = result['review'].upper().count('CRITICAL')
            high = result['review'].upper().count('HIGH')
            medium = result['review'].upper().count('MEDIUM')
            total = critical + high + medium

            if total == 0:
                output.append("✅ No issues found in this file.\n\n")
            else:
                output.append(f"**Found {total} issue(s)** ")
                badges = []
                if critical > 0:
                    badges.append(f"🔴 {critical} Critical")
                if high > 0:
                    badges.append(f"🟠 {high} High")
                if medium > 0:
                    badges.append(f"🟡 {medium} Medium")
                output.append(" | ".join(badges) + "\n\n")

                # Collapsible details
                output.append("<details>\n")
                output.append("<summary>📖 Click to view detailed review</summary>\n\n")
                output.append(result['review'])
                output.append("\n\n</details>\n\n")

        output.append("---\n\n")

    # Footer
    output.append("## 🤖 About This Review\n\n")
    output.append("This automated review was performed by the **Python Codebase Reviewer** GitHub App.\n\n")
    output.append("**Review Capabilities**:\n")
    output.append("- 🔒 Security: OWASP Top 10 vulnerabilities\n")
    output.append("- 🏗️ Architecture: SOLID principles, design patterns\n")
    output.append("- ✨ Code Quality: PEP standards, Pythonic idioms\n")
    output.append("- ⚡ Performance: Algorithm complexity, N+1 queries\n")
    output.append("- 🐍 Python Expertise: Standard library, frameworks, modern features\n")

    return ''.join(output)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({
        'status': 'healthy',
        'service': 'python-codebase-reviewer',
        'version': '1.0.0'
    }), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle GitHub webhook events.

    Supported events:
    - pull_request (opened, synchronize, reopened)
    """
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_webhook_signature(request.data, signature):
        logger.warning("⚠️  Webhook signature verification failed")
        return jsonify({'error': 'Invalid signature'}), 401

    # Get event type
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    logger.info(f"📥 Received {event} event")

    # Handle pull request events
    if event == 'pull_request':
        action = payload['action']

        # Only process these actions
        if action not in ['opened', 'synchronize', 'reopened']:
            logger.info(f"ℹ️  Ignoring PR action: {action}")
            return jsonify({'status': 'ignored'}), 200

        try:
            # Extract PR information
            installation_id = payload['installation']['id']
            repo = payload['repository']['full_name']
            pr_number = payload['pull_request']['number']
            pr_title = payload['pull_request']['title']

            logger.info(f"🔍 Processing PR #{pr_number}: {pr_title}")
            logger.info(f"   Repository: {repo}")
            logger.info(f"   Action: {action}")

            # Get installation token
            logger.info("🔑 Getting installation access token...")
            token = get_installation_access_token(installation_id)

            # Fetch PR files with content
            logger.info("📥 Fetching PR files...")
            files = fetch_pr_files_with_content(repo, pr_number, token)

            # Filter to Python files only
            python_files = [f for f in files if f['filename'].endswith('.py')]

            if not python_files:
                logger.info("ℹ️  No Python files to review")
                return jsonify({'status': 'no_python_files'}), 200

            logger.info(f"📝 Found {len(python_files)} Python files to review")

            # Run code review
            review_result = run_code_review(python_files, repo, pr_number)

            # Post review comment
            logger.info("💬 Posting review comment...")
            os.environ['GITHUB_TOKEN'] = token
            post_pr_comment(repo, pr_number, review_result)

            logger.info(f"✅ Successfully reviewed PR #{pr_number}")

            return jsonify({
                'status': 'success',
                'pr_number': pr_number,
                'files_reviewed': len(python_files)
            }), 200

        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    elif event == 'ping':
        logger.info("🏓 Received ping event")
        return jsonify({'status': 'pong'}), 200

    else:
        logger.info(f"ℹ️  Unsupported event type: {event}")
        return jsonify({'status': 'unsupported_event'}), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint."""
    return jsonify({
        'service': 'Python Codebase Reviewer - GitHub App',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'webhook': '/webhook'
        }
    }), 200


if __name__ == '__main__':
    # Validate configuration
    if missing_vars:
        logger.error("❌ Cannot start - missing required environment variables")
        logger.error(f"   Missing: {', '.join(missing_vars)}")
        sys.exit(1)

    # Get port from environment (Cloud Run sets PORT)
    port = int(os.getenv('PORT', 8080))

    logger.info("=" * 60)
    logger.info("🚀 Starting Python Codebase Reviewer GitHub App")
    logger.info("=" * 60)
    logger.info(f"   Port: {port}")
    logger.info(f"   GitHub App ID: {GITHUB_APP_ID}")
    logger.info(f"   Webhook Secret: {'✓ Set' if GITHUB_WEBHOOK_SECRET else '✗ Not set'}")
    logger.info(f"   Private Key: {'✓ Set' if GITHUB_PRIVATE_KEY else '✗ Not set'}")
    logger.info(f"   Google API Key: {'✓ Set' if GOOGLE_API_KEY else '✗ Not set'}")
    logger.info("=" * 60)

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
