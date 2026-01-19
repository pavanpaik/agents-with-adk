"""
GitHub App webhook handler for Python Codebase Reviewer.

This Flask application receives webhook events from GitHub and runs
code reviews on pull requests automatically using the agent-driven MCP approach.

Production-ready features:
- Webhook signature verification
- GitHub App authentication (JWT + installation tokens)
- Agent-driven review using GitHub MCP tools
- Error handling and logging
- Health checks

With MCP, the agent autonomously:
- Fetches PR files using get_pull_request_files
- Fetches file contents using get_file_contents
- Reviews code with specialized agents
- Posts reviews using create_pull_request_review
"""
import os
import sys
import hmac
import hashlib
import logging
import time
import uuid

from flask import Flask, request, jsonify, g
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
    logger.info("✅ Successfully imported Python Codebase Reviewer")
except ImportError as e:
    logger.error(f"❌ Failed to import Python Codebase Reviewer: {e}")
    logger.error("Make sure the package is installed: pip install -e .")

# Initialize Flask app
app = Flask(__name__)

# Configuration from environment
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

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
    # In production, fail fast
    if ENVIRONMENT == 'production':
        logger.critical("🔴 Cannot start in production with missing environment variables")
        sys.exit(1)


@app.before_request
def before_request():
    """Add request ID for tracking."""
    g.request_id = str(uuid.uuid4())
    logger.info(f"[{g.request_id}] Request started: {request.method} {request.path}")


def verify_webhook_signature(payload_body: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature.

    Args:
        payload_body: Raw request body as bytes
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')

    # In production, webhook secret MUST be set
    if not webhook_secret:
        if ENVIRONMENT == 'production':
            logger.critical("🔴 GITHUB_WEBHOOK_SECRET not set in production!")
            raise RuntimeError("GITHUB_WEBHOOK_SECRET must be set in production")
        else:
            logger.warning("⚠️  GITHUB_WEBHOOK_SECRET not set - signature verification disabled (development only)")
            return True

    if not signature:
        logger.warning("⚠️  No signature provided in request")
        return False

    # Compute expected signature
    expected = 'sha256=' + hmac.new(
        webhook_secret.encode(),
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
    app_id = os.getenv('GITHUB_APP_ID')
    private_key = os.getenv('GITHUB_PRIVATE_KEY')

    now = int(time.time())

    payload = {
        'iat': now,
        'exp': now + 600,  # Token expires in 10 minutes
        'iss': app_id
    }

    # Sign with private key
    token = jwt.encode(payload, private_key, algorithm='RS256')

    return token


def get_installation_access_token(installation_id: int) -> str:
    """
    Get installation access token for GitHub App.

    Args:
        installation_id: GitHub App installation ID

    Returns:
        Access token string
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


def run_agent_review(repo: str, pr_number: int, token: str) -> str:
    """
    Run code review using agent with GitHub MCP tools.

    The agent autonomously handles:
    - Fetching PR files (get_pull_request_files)
    - Fetching file contents (get_file_contents)
    - Reviewing with specialized agents
    - Posting the review (create_pull_request_review or create_issue_comment)

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
        token: GitHub installation access token

    Returns:
        Agent's response describing what it did
    """
    logger.info(f"🤖 Delegating to AI agent with GitHub MCP tools...")

    # Set the GitHub token for MCP tools
    os.environ['GITHUB_TOKEN'] = token

    # Create natural language task for the agent
    task = f"""
You are handling a GitHub pull request webhook event.

**Repository**: {repo}
**Pull Request**: #{pr_number}

**Your task:**
1. Use `get_pull_request_files` MCP tool to fetch all changed files in the PR
2. Filter to Python files only (*.py)
3. For each Python file, use `get_file_contents` to fetch the file content
4. Review each file using your specialized reviewer agents:
   - Security vulnerabilities (OWASP Top 10)
   - Architecture issues (SOLID principles)
   - Code quality (PEP 8, Pythonic idioms)
   - Performance issues (complexity, N+1 queries)
   - Python best practices

5. Generate a comprehensive markdown review report with:
   - Executive summary with severity counts (Critical/High/Medium/Low)
   - File-by-file breakdown with specific issues
   - Line numbers and code snippets where applicable
   - Suggested fixes
   - Severity indicators (🔴 Critical, 🟠 High, 🟡 Medium, 🔵 Low)

6. Post your review to the pull request using `create_issue_comment` MCP tool

**Important:**
- If no Python files are changed, post a brief comment saying so
- Include a footer explaining this is an automated review
- Be specific and actionable in your findings
- Focus on issues that matter (security, bugs, design flaws)

Begin your review now.
"""

    try:
        logger.info("⏳ Agent review in progress...")
        response = root_agent.run(task)
        logger.info("✅ Agent completed review and posted to PR")
        return response

    except Exception as e:
        logger.error(f"❌ Error during agent review: {e}", exc_info=True)
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({
        'status': 'healthy',
        'service': 'python-codebase-reviewer-github-app',
        'version': '2.0.0-mcp',
        'mcp_enabled': True
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
        return jsonify({'error': 'Invalid signature'}), 403

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

            # Run agent-driven review with MCP tools
            agent_response = run_agent_review(repo, pr_number, token)

            logger.info(f"✅ Successfully processed PR #{pr_number}")

            return jsonify({
                'status': 'success',
                'pr_number': pr_number,
                'repository': repo,
                'agent_response': agent_response[:200] + '...' if len(agent_response) > 200 else agent_response
            }), 200

        except (KeyError, TypeError) as e:
            logger.error(f"❌ Malformed webhook payload: {e}", exc_info=True)
            return jsonify({'error': 'Malformed payload'}), 400

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error: {e}", exc_info=True)
            return jsonify({'error': 'Network error communicating with GitHub'}), 502

        except Exception as e:
            logger.critical(f"❌ Unexpected error processing webhook: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

    elif event == 'ping':
        logger.info("🏓 Received ping event")
        return jsonify({
            'status': 'pong',
            'message': 'Python Codebase Reviewer GitHub App is running with MCP support'
        }), 200

    else:
        logger.info(f"ℹ️  Unsupported event type: {event}")
        return jsonify({'status': 'unsupported_event'}), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint."""
    return jsonify({
        'service': 'Python Codebase Reviewer - GitHub App',
        'version': '2.0.0-mcp',
        'status': 'running',
        'mcp_enabled': True,
        'features': [
            'Agent-driven code review',
            'GitHub MCP tool integration',
            'Automated PR reviews',
            'Security vulnerability detection',
            'Architecture analysis',
            'Code quality assessment',
            'Performance optimization'
        ],
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
    logger.info("🚀 Starting Python Codebase Reviewer GitHub App (MCP)")
    logger.info("=" * 60)
    logger.info(f"   Port: {port}")
    logger.info(f"   GitHub App ID: {GITHUB_APP_ID}")
    logger.info(f"   Webhook Secret: {'✓ Set' if GITHUB_WEBHOOK_SECRET else '✗ Not set'}")
    logger.info(f"   Private Key: {'✓ Set' if GITHUB_PRIVATE_KEY else '✗ Not set'}")
    logger.info(f"   Google API Key: {'✓ Set' if GOOGLE_API_KEY else '✗ Not set'}")
    logger.info(f"   MCP Enabled: ✓ Yes")
    logger.info("=" * 60)

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
