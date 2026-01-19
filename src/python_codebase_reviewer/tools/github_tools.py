"""
GitHub integration tools for Python Codebase Reviewer agents.

These tools enable agents to interact with GitHub repositories and pull requests.
"""
import os
import requests
from typing import List, Dict, Optional
import base64
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logger = logging.getLogger(__name__)

GITHUB_API = 'https://api.github.com'


class GitHubAPIError(Exception):
    """GitHub API error."""
    pass


def _get_github_token() -> str:
    """
    Get GitHub token from environment.

    Returns:
        GitHub token string

    Raises:
        GitHubAPIError: If token not set
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        logger.error("GITHUB_TOKEN environment variable not set")
        raise GitHubAPIError("GITHUB_TOKEN environment variable not set")
    return token


def _create_session() -> requests.Session:
    """
    Create requests session with retry logic.

    Returns:
        Configured requests.Session with exponential backoff
    """
    session = requests.Session()

    # Configure retry strategy with exponential backoff
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,  # 1s, 2s, 4s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def _validate_repo(repo: str) -> None:
    """
    Validate repository format.

    Args:
        repo: Repository string

    Raises:
        ValueError: If repo format is invalid
    """
    if not repo or not isinstance(repo, str):
        raise ValueError("repo must be a non-empty string")
    if '/' not in repo or repo.count('/') != 1:
        raise ValueError("repo must be in 'owner/repo' format")
    owner, name = repo.split('/')
    if not owner or not name:
        raise ValueError("repo must be in 'owner/repo' format with non-empty owner and name")


def _validate_pr_number(pr_number: int) -> None:
    """
    Validate pull request number.

    Args:
        pr_number: PR number

    Raises:
        ValueError: If pr_number is invalid
    """
    if not isinstance(pr_number, int) or pr_number < 1:
        raise ValueError("pr_number must be a positive integer")


def github_request(method: str, endpoint: str, data: Optional[Dict] = None):
    """
    Make authenticated GitHub API request with retry logic.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint (e.g., '/repos/owner/repo/pulls/123')
        data: Request body for POST/PUT/PATCH

    Returns:
        JSON response from GitHub API

    Raises:
        GitHubAPIError: If request fails
        ValueError: If method is unsupported
    """
    github_token = _get_github_token()

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    url = f'{GITHUB_API}/{endpoint.lstrip("/")}'

    logger.info(f"GitHub API request: {method} {endpoint}")

    try:
        session = _create_session()

        if method == 'GET':
            response = session.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            response = session.post(url, headers=headers, json=data, timeout=30)
        elif method == 'PUT':
            response = session.put(url, headers=headers, json=data, timeout=30)
        elif method == 'PATCH':
            response = session.patch(url, headers=headers, json=data, timeout=30)
        elif method == 'DELETE':
            response = session.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f'Unsupported HTTP method: {method}')

        response.raise_for_status()

        logger.debug(f"GitHub API response: {response.status_code} for {method} {endpoint}")

        try:
            return response.json() if response.text else {}
        except ValueError as e:
            logger.error(f"Invalid JSON in response from {method} {endpoint}: {str(e)}")
            raise GitHubAPIError(f'Invalid JSON in GitHub API response: {str(e)}')

    except requests.exceptions.HTTPError as e:
        logger.error(f"GitHub API HTTP error: {method} {endpoint} - {response.status_code}: {str(e)}")
        raise GitHubAPIError(f'GitHub API request failed: HTTP {response.status_code} - {str(e)}')
    except requests.exceptions.Timeout as e:
        logger.error(f"GitHub API timeout: {method} {endpoint} - {str(e)}")
        raise GitHubAPIError(f'GitHub API request timed out: {str(e)}')
    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request error: {method} {endpoint} - {str(e)}")
        raise GitHubAPIError(f'GitHub API request failed: {str(e)}')


def fetch_pr_files(repo: str, pr_number: int) -> List[Dict]:
    """
    Fetch list of files changed in a pull request with pagination support.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number

    Returns:
        List of file objects with:
        - filename: File path
        - status: "added", "modified", "removed", etc.
        - additions: Number of lines added
        - deletions: Number of lines deleted
        - changes: Total changes
        - patch: Git diff patch for the file

    Raises:
        ValueError: If repo or pr_number format is invalid
        GitHubAPIError: If API request fails

    Example:
        >>> files = fetch_pr_files("owner/repo", 123)
        >>> for file in files:
        ...     print(f"{file['filename']}: +{file['additions']} -{file['deletions']}")
    """
    # Validate inputs
    _validate_repo(repo)
    _validate_pr_number(pr_number)

    logger.info(f"Fetching files for PR #{pr_number} in {repo}")

    # Fetch all pages
    all_files = []
    page = 1

    while True:
        endpoint = f'/repos/{repo}/pulls/{pr_number}/files?page={page}&per_page=100'
        files = github_request('GET', endpoint)

        if not files:
            break

        all_files.extend(files)
        page += 1

        if len(files) < 100:  # Last page
            break

    # Filter to Python files only
    python_files = [f for f in all_files if f['filename'].endswith('.py')]

    logger.info(f"Found {len(python_files)} Python files (out of {len(all_files)} total files)")

    return python_files


def fetch_file_content(repo: str, path: str, ref: str = 'main') -> str:
    """
    Fetch content of a file from repository.

    Args:
        repo: Repository in format "owner/repo"
        path: File path in repository
        ref: Branch, tag, or commit SHA (default: 'main')

    Returns:
        File content as string

    Raises:
        ValueError: If repo format is invalid or path is empty
        GitHubAPIError: If API request fails or file not found

    Example:
        >>> content = fetch_file_content("owner/repo", "src/main.py", "main")
        >>> print(content)
    """
    # Validate inputs
    _validate_repo(repo)
    if not path or not isinstance(path, str):
        raise ValueError("path must be a non-empty string")

    logger.info(f"Fetching content for {path} in {repo} (ref: {ref})")

    endpoint = f'/repos/{repo}/contents/{path}?ref={ref}'
    response = github_request('GET', endpoint)

    # Decode base64 content
    if 'content' in response:
        content = base64.b64decode(response['content']).decode('utf-8')
        logger.debug(f"Successfully decoded content for {path} ({len(content)} chars)")
        return content
    else:
        logger.error(f"No content found for {path} in response")
        raise GitHubAPIError(f'No content found for {path}')


def fetch_pr_diff(repo: str, pr_number: int) -> str:
    """
    Fetch the full diff of a pull request.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number

    Returns:
        Full git diff as string

    Raises:
        ValueError: If repo or pr_number format is invalid
        GitHubAPIError: If API request fails
    """
    # Validate inputs
    _validate_repo(repo)
    _validate_pr_number(pr_number)

    github_token = _get_github_token()

    logger.info(f"Fetching diff for PR #{pr_number} in {repo}")

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.diff'  # Request diff format
    }

    url = f'{GITHUB_API}/repos/{repo}/pulls/{pr_number}'

    try:
        session = _create_session()
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.debug(f"Successfully fetched diff for PR #{pr_number} ({len(response.text)} chars)")
        return response.text
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to fetch PR diff: HTTP {response.status_code} - {str(e)}")
        raise GitHubAPIError(f'Failed to fetch PR diff: HTTP {response.status_code} - {str(e)}')
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout fetching PR diff: {str(e)}")
        raise GitHubAPIError(f'Timeout fetching PR diff: {str(e)}')
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch PR diff: {str(e)}")
        raise GitHubAPIError(f'Failed to fetch PR diff: {str(e)}')


def fetch_pr_info(repo: str, pr_number: int) -> Dict:
    """
    Fetch pull request information.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number

    Returns:
        PR information including title, body, author, etc.

    Raises:
        ValueError: If repo or pr_number format is invalid
        GitHubAPIError: If API request fails
    """
    # Validate inputs
    _validate_repo(repo)
    _validate_pr_number(pr_number)

    logger.info(f"Fetching info for PR #{pr_number} in {repo}")

    endpoint = f'/repos/{repo}/pulls/{pr_number}'
    return github_request('GET', endpoint)


def post_pr_review(
    repo: str,
    pr_number: int,
    body: str,
    event: str = 'COMMENT',
    comments: Optional[List[Dict]] = None
) -> Dict:
    """
    Post a code review on a pull request.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
        body: Review summary/body
        event: Review event type:
            - 'COMMENT': General comment
            - 'APPROVE': Approve the PR
            - 'REQUEST_CHANGES': Request changes
        comments: List of inline review comments with:
            - path: File path
            - line: Line number
            - body: Comment text

    Returns:
        Review object

    Raises:
        ValueError: If inputs are invalid
        GitHubAPIError: If API request fails

    Example:
        >>> post_pr_review(
        ...     "owner/repo",
        ...     123,
        ...     "Found 3 security issues",
        ...     event='REQUEST_CHANGES',
        ...     comments=[{
        ...         'path': 'src/auth.py',
        ...         'line': 10,
        ...         'body': 'SQL injection vulnerability here'
        ...     }]
        ... )
    """
    # Validate inputs
    _validate_repo(repo)
    _validate_pr_number(pr_number)
    if not body or not isinstance(body, str):
        raise ValueError("body must be a non-empty string")
    if event not in ['COMMENT', 'APPROVE', 'REQUEST_CHANGES']:
        raise ValueError("event must be one of: COMMENT, APPROVE, REQUEST_CHANGES")

    logger.info(f"Posting review on PR #{pr_number} in {repo} (event: {event})")

    endpoint = f'/repos/{repo}/pulls/{pr_number}/reviews'

    data = {
        'body': body,
        'event': event
    }

    if comments:
        # Format comments for GitHub API
        data['comments'] = [
            {
                'path': c['path'],
                'line': c.get('line', c.get('position')),
                'body': c['body']
            }
            for c in comments
        ]
        logger.debug(f"Including {len(comments)} inline comments")

    return github_request('POST', endpoint, data)


def post_pr_comment(repo: str, pr_number: int, body: str) -> Dict:
    """
    Post a general comment on a pull request (not a review).

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
        body: Comment text (supports GitHub-flavored Markdown)

    Returns:
        Comment object

    Raises:
        ValueError: If inputs are invalid
        GitHubAPIError: If API request fails

    Example:
        >>> post_pr_comment(
        ...     "owner/repo",
        ...     123,
        ...     "# Code Review Results\n\n✅ All checks passed!"
        ... )
    """
    # Validate inputs
    _validate_repo(repo)
    _validate_pr_number(pr_number)
    if not body or not isinstance(body, str):
        raise ValueError("body must be a non-empty string")

    logger.info(f"Posting comment on PR #{pr_number} in {repo}")

    # GitHub uses /issues endpoint for PR comments
    endpoint = f'/repos/{repo}/issues/{pr_number}/comments'
    data = {'body': body}
    return github_request('POST', endpoint, data)


def create_review_comment(
    repo: str,
    pr_number: int,
    commit_id: str,
    path: str,
    line: int,
    body: str
) -> Dict:
    """
    Create a single review comment on a specific line.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number
        commit_id: SHA of the commit to comment on
        path: File path
        line: Line number
        body: Comment text

    Returns:
        Review comment object

    Raises:
        ValueError: If inputs are invalid
        GitHubAPIError: If API request fails
    """
    # Validate inputs
    _validate_repo(repo)
    _validate_pr_number(pr_number)
    if not commit_id or not isinstance(commit_id, str):
        raise ValueError("commit_id must be a non-empty string")
    if not path or not isinstance(path, str):
        raise ValueError("path must be a non-empty string")
    if not isinstance(line, int) or line < 1:
        raise ValueError("line must be a positive integer")
    if not body or not isinstance(body, str):
        raise ValueError("body must be a non-empty string")

    logger.info(f"Creating review comment on {path}:{line} for PR #{pr_number} in {repo}")

    endpoint = f'/repos/{repo}/pulls/{pr_number}/comments'
    data = {
        'body': body,
        'commit_id': commit_id,
        'path': path,
        'line': line
    }
    return github_request('POST', endpoint, data)


# Export tools for ADK agents (optional - if you want to use these as agent tools)
try:
    from google.adk.tools import Tool

    fetch_pr_files_tool = Tool(
        name="fetch_pr_files",
        description="Fetch list of Python files changed in a GitHub pull request",
        function=fetch_pr_files
    )

    fetch_file_content_tool = Tool(
        name="fetch_file_content",
        description="Fetch content of a file from GitHub repository",
        function=fetch_file_content
    )

    fetch_pr_diff_tool = Tool(
        name="fetch_pr_diff",
        description="Fetch the full diff of a GitHub pull request",
        function=fetch_pr_diff
    )

    fetch_pr_info_tool = Tool(
        name="fetch_pr_info",
        description="Fetch pull request information (title, description, author, etc.)",
        function=fetch_pr_info
    )

    post_pr_review_tool = Tool(
        name="post_pr_review",
        description="Post a code review on a GitHub pull request with optional inline comments",
        function=post_pr_review
    )

    post_pr_comment_tool = Tool(
        name="post_pr_comment",
        description="Post a general comment on a GitHub pull request",
        function=post_pr_comment
    )

except ImportError:
    # ADK not installed - tools can still be used as regular Python functions
    pass


__all__ = [
    'fetch_pr_files',
    'fetch_file_content',
    'fetch_pr_diff',
    'fetch_pr_info',
    'post_pr_review',
    'post_pr_comment',
    'create_review_comment',
    'GitHubAPIError',
]
