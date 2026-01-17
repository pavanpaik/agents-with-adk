"""
GitHub integration tools for Python Codebase Reviewer agents.

These tools enable agents to interact with GitHub repositories and pull requests.
"""
import os
import requests
from typing import List, Dict, Optional
import base64

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_API = 'https://api.github.com'


class GitHubAPIError(Exception):
    """GitHub API error."""
    pass


def github_request(method: str, endpoint: str, data: Optional[Dict] = None):
    """
    Make authenticated GitHub API request.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint (e.g., '/repos/owner/repo/pulls/123')
        data: Request body for POST/PUT/PATCH

    Returns:
        JSON response from GitHub API

    Raises:
        GitHubAPIError: If request fails
    """
    if not GITHUB_TOKEN:
        raise GitHubAPIError("GITHUB_TOKEN environment variable not set")

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    url = f'{GITHUB_API}/{endpoint.lstrip("/")}'

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f'Unsupported HTTP method: {method}')

        response.raise_for_status()
        return response.json() if response.text else {}

    except requests.exceptions.RequestException as e:
        raise GitHubAPIError(f'GitHub API request failed: {str(e)}')


def fetch_pr_files(repo: str, pr_number: int) -> List[Dict]:
    """
    Fetch list of files changed in a pull request.

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

    Example:
        >>> files = fetch_pr_files("owner/repo", 123)
        >>> for file in files:
        ...     print(f"{file['filename']}: +{file['additions']} -{file['deletions']}")
    """
    endpoint = f'/repos/{repo}/pulls/{pr_number}/files'
    files = github_request('GET', endpoint)

    # Filter to Python files only
    python_files = [f for f in files if f['filename'].endswith('.py')]

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

    Example:
        >>> content = fetch_file_content("owner/repo", "src/main.py", "main")
        >>> print(content)
    """
    endpoint = f'/repos/{repo}/contents/{path}?ref={ref}'
    response = github_request('GET', endpoint)

    # Decode base64 content
    if 'content' in response:
        return base64.b64decode(response['content']).decode('utf-8')
    else:
        raise GitHubAPIError(f'No content found for {path}')


def fetch_pr_diff(repo: str, pr_number: int) -> str:
    """
    Fetch the full diff of a pull request.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number

    Returns:
        Full git diff as string
    """
    if not GITHUB_TOKEN:
        raise GitHubAPIError("GITHUB_TOKEN environment variable not set")

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.diff'  # Request diff format
    }

    url = f'{GITHUB_API}/repos/{repo}/pulls/{pr_number}'

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise GitHubAPIError(f'Failed to fetch PR diff: {str(e)}')


def fetch_pr_info(repo: str, pr_number: int) -> Dict:
    """
    Fetch pull request information.

    Args:
        repo: Repository in format "owner/repo"
        pr_number: Pull request number

    Returns:
        PR information including title, body, author, etc.
    """
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

    Example:
        >>> post_pr_comment(
        ...     "owner/repo",
        ...     123,
        ...     "# Code Review Results\n\n✅ All checks passed!"
        ... )
    """
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
    """
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
