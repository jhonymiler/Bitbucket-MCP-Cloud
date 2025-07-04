#!/usr/bin/env python3
"""
Bitbucket Cloud MCP Server
Complete MCP server for Bitbucket Cloud API interactions using the official MCP library
"""

from datetime import datetime
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import our custom models and utilities
try:
    # Try local import first (when running locally)
    from src.models import (
        BitbucketBranch,
        BitbucketComment,
        BitbucketProject,
        BitbucketPullRequest,
        BitbucketRepository,
        BitbucketUser,
    )
    from src.utils import get_env_var, setup_logger
except ImportError:
    # Fallback to package import (when installed via pip/uvx)
    from bitbucket_mcp_cloud.models import (
        BitbucketBranch,
        BitbucketComment,
        BitbucketProject,
        BitbucketPullRequest,
        BitbucketRepository,
        BitbucketUser,
    )
    from bitbucket_mcp_cloud.utils import get_env_var, setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)


# Complete HTTP client for Bitbucket API
class BitbucketCloudClient:
    """Complete Bitbucket Cloud API client with all required methods"""

    def __init__(self) -> None:
        self.username = get_env_var("BITBUCKET_USERNAME")
        self.app_password = get_env_var("BITBUCKET_TOKEN")
        self.default_workspace = get_env_var("BITBUCKET_DEFAULT_WORKSPACE")
        self.base_url = "https://api.bitbucket.org/2.0"
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BitbucketCloudClient":
        self._client = httpx.AsyncClient(follow_redirects=True)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._client:
            await self._client.aclose()

    def _get_auth(self) -> tuple[str, str]:
        return (self.username, self.app_password)

    def _get_workspace(self, workspace: str | None = None) -> str:
        return workspace or self.default_workspace

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Make authenticated request to Bitbucket API"""
        url = f"{self.base_url}{endpoint}"
        auth = self._get_auth()

        try:
            if self._client is None:
                raise RuntimeError("Client not initialized")
            response = await self._client.request(method, url, auth=auth, **kwargs)
            response.raise_for_status()
            json_response = response.json()
            if not isinstance(json_response, dict):
                return {}
            return json_response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise

    async def _request_text(self, method: str, endpoint: str, **kwargs: Any) -> str:
        """Make authenticated request to Bitbucket API and return text response"""
        url = f"{self.base_url}{endpoint}"
        auth = self._get_auth()

        try:
            if self._client is None:
                raise RuntimeError("Client not initialized")
            response = await self._client.request(method, url, auth=auth, **kwargs)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise

    # Projects
    async def list_projects(
        self, workspace: str | None = None, limit: int = 25, start: int = 0
    ) -> list[BitbucketProject]:
        """List projects in workspace"""
        workspace = self._get_workspace(workspace)
        endpoint = f"/workspaces/{workspace}/projects"
        params = {"pagelen": limit, "page": start // limit + 1}

        data = await self._request("GET", endpoint, params=params)
        projects = []

        for item in data.get("values", []):
            projects.append(
                BitbucketProject(
                    uuid=item.get("uuid"),
                    key=item.get("key"),
                    name=item.get("name"),
                    description=item.get("description"),
                    is_private=item.get("is_private", False),
                    created_on=(
                        datetime.fromisoformat(
                            item.get("created_on").replace("Z", "+00:00")
                        )
                        if item.get("created_on")
                        else None
                    ),
                    updated_on=(
                        datetime.fromisoformat(
                            item.get("updated_on").replace("Z", "+00:00")
                        )
                        if item.get("updated_on")
                        else None
                    ),
                )
            )

        return projects

    # Repositories
    async def list_repositories(
        self,
        workspace: str | None = None,
        project: str | None = None,
        limit: int = 25,
        start: int = 0,
    ) -> list[BitbucketRepository]:
        """List repositories in workspace or project"""
        workspace = self._get_workspace(workspace)

        if project:
            endpoint = f"/repositories/{workspace}"
            params = {
                "q": f'project.key="{project}"',
                "pagelen": limit,
                "page": start // limit + 1,
            }
        else:
            endpoint = f"/repositories/{workspace}"
            params = {"pagelen": limit, "page": start // limit + 1}

        data = await self._request("GET", endpoint, params=params)
        repositories = []

        for item in data.get("values", []):
            repositories.append(
                BitbucketRepository(
                    uuid=item.get("uuid"),
                    name=item.get("name"),
                    full_name=item.get("full_name"),
                    description=item.get("description"),
                    is_private=item.get("is_private", False),
                    clone_links=item.get("links", {}).get("clone", []),
                    size=item.get("size"),
                    language=item.get("language"),
                    created_on=(
                        datetime.fromisoformat(
                            item.get("created_on").replace("Z", "+00:00")
                        )
                        if item.get("created_on")
                        else None
                    ),
                    updated_on=(
                        datetime.fromisoformat(
                            item.get("updated_on").replace("Z", "+00:00")
                        )
                        if item.get("updated_on")
                        else None
                    ),
                )
            )

        return repositories

    # Pull Requests
    async def list_pull_requests(
        self,
        repository: str,
        workspace: str | None = None,
        state: str = "OPEN",
        limit: int = 25,
    ) -> list[BitbucketPullRequest]:
        """List pull requests for repository"""
        workspace = self._get_workspace(workspace)
        endpoint = f"/repositories/{workspace}/{repository}/pullrequests"
        params = {"state": state, "pagelen": limit}

        data = await self._request("GET", endpoint, params=params)
        pull_requests = []

        for item in data.get("values", []):
            author_data = item.get("author")
            author = None
            if author_data:
                author = BitbucketUser(
                    uuid=author_data.get("uuid"),
                    username=author_data.get("username"),
                    display_name=author_data.get("display_name"),
                    account_id=author_data.get("account_id"),
                    nickname=author_data.get("nickname"),
                )

            source_data = item.get("source", {}).get("branch")
            source = (
                BitbucketBranch(name=source_data.get("name")) if source_data else None
            )

            dest_data = item.get("destination", {}).get("branch")
            destination = (
                BitbucketBranch(name=dest_data.get("name")) if dest_data else None
            )

            pull_requests.append(
                BitbucketPullRequest(
                    id=item.get("id"),
                    title=item.get("title"),
                    description=item.get("description"),
                    state=item.get("state"),
                    author=author,
                    source=source,
                    destination=destination,
                    created_on=(
                        datetime.fromisoformat(
                            item.get("created_on").replace("Z", "+00:00")
                        )
                        if item.get("created_on")
                        else None
                    ),
                    updated_on=(
                        datetime.fromisoformat(
                            item.get("updated_on").replace("Z", "+00:00")
                        )
                        if item.get("updated_on")
                        else None
                    ),
                    close_source_branch=item.get("close_source_branch", False),
                    reviewers=item.get("reviewers", []),
                    participants=item.get("participants", []),
                )
            )

        return pull_requests

    async def get_pull_request(
        self, repository: str, pr_id: int, workspace: str | None = None
    ) -> BitbucketPullRequest:
        """Get specific pull request details"""
        workspace = self._get_workspace(workspace)
        endpoint = f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}"

        item = await self._request("GET", endpoint)

        author_data = item.get("author")
        author = None
        if author_data:
            author = BitbucketUser(
                uuid=author_data.get("uuid"),
                username=author_data.get("username"),
                display_name=author_data.get("display_name"),
                account_id=author_data.get("account_id"),
                nickname=author_data.get("nickname"),
            )

        source_data = item.get("source", {}).get("branch")
        source = BitbucketBranch(name=source_data.get("name")) if source_data else None

        dest_data = item.get("destination", {}).get("branch")
        destination = BitbucketBranch(name=dest_data.get("name")) if dest_data else None

        return BitbucketPullRequest(
            id=item.get("id") or 0,
            title=item.get("title") or "",
            description=item.get("description"),
            state=item.get("state") or "",
            author=author,
            source=source,
            destination=destination,
            created_on=(
                datetime.fromisoformat(
                    item.get("created_on", "").replace("Z", "+00:00")
                )
                if item.get("created_on")
                else None
            ),
            updated_on=(
                datetime.fromisoformat(
                    item.get("updated_on", "").replace("Z", "+00:00")
                )
                if item.get("updated_on")
                else None
            ),
            close_source_branch=item.get("close_source_branch", False),
            reviewers=item.get("reviewers", []),
            participants=item.get("participants", []),
        )

    async def create_pull_request(
        self,
        repository: str,
        title: str,
        source_branch: str,
        target_branch: str = "main",
        description: str = "",
        workspace: str | None = None,
        close_source_branch: bool = False,
        reviewers: list[str] | None = None,
    ) -> BitbucketPullRequest:
        """Create new pull request"""
        workspace = self._get_workspace(workspace)
        endpoint = f"/repositories/{workspace}/{repository}/pullrequests"

        data = {
            "title": title,
            "description": description,
            "source": {"branch": {"name": source_branch}},
            "destination": {"branch": {"name": target_branch}},
            "close_source_branch": close_source_branch,
        }

        if reviewers:
            data["reviewers"] = [{"uuid": reviewer} for reviewer in reviewers]

        item = await self._request("POST", endpoint, json=data)

        # Convert response to BitbucketPullRequest model
        author_data = item.get("author")
        author = None
        if author_data:
            author = BitbucketUser(
                uuid=author_data.get("uuid"),
                username=author_data.get("username"),
                display_name=author_data.get("display_name"),
                account_id=author_data.get("account_id"),
                nickname=author_data.get("nickname"),
            )

        return BitbucketPullRequest(
            id=item.get("id") or 0,
            title=item.get("title") or "",
            description=item.get("description"),
            state=item.get("state") or "",
            author=author,
            created_on=(
                datetime.fromisoformat(
                    item.get("created_on", "").replace("Z", "+00:00")
                )
                if item.get("created_on")
                else None
            ),
            updated_on=(
                datetime.fromisoformat(
                    item.get("updated_on", "").replace("Z", "+00:00")
                )
                if item.get("updated_on")
                else None
            ),
        )

    async def approve_pull_request(
        self, repository: str, pr_id: int, workspace: str | None = None
    ) -> dict[str, Any]:
        """Approve pull request"""
        workspace = self._get_workspace(workspace)
        endpoint = (
            f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/approve"
        )

        return await self._request("POST", endpoint)

    async def decline_pull_request(
        self, repository: str, pr_id: int, workspace: str | None = None
    ) -> dict[str, Any]:
        """Decline pull request"""
        workspace = self._get_workspace(workspace)
        endpoint = (
            f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/decline"
        )

        return await self._request("POST", endpoint)

    async def merge_pull_request(
        self,
        repository: str,
        pr_id: int,
        merge_strategy: str = "merge_commit",
        workspace: str | None = None,
    ) -> dict[str, Any]:
        """Merge approved pull request"""
        workspace = self._get_workspace(workspace)
        endpoint = f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/merge"

        data = {"merge_strategy": merge_strategy}
        return await self._request("POST", endpoint, json=data)

    # Comments
    async def list_pull_request_comments(
        self, repository: str, pr_id: int, workspace: str | None = None
    ) -> list[BitbucketComment]:
        """List comments on pull request"""
        workspace = self._get_workspace(workspace)
        endpoint = (
            f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/comments"
        )

        data = await self._request("GET", endpoint)
        comments = []

        for item in data.get("values", []):
            user_data = item.get("user")
            user = None
            if user_data:
                user = BitbucketUser(
                    uuid=user_data.get("uuid"),
                    username=user_data.get("username"),
                    display_name=user_data.get("display_name"),
                    account_id=user_data.get("account_id"),
                    nickname=user_data.get("nickname"),
                )

            comments.append(
                BitbucketComment(
                    id=item.get("id"),
                    content=item.get("content", {}),
                    user=user,
                    created_on=(
                        datetime.fromisoformat(
                            item.get("created_on").replace("Z", "+00:00")
                        )
                        if item.get("created_on")
                        else None
                    ),
                    updated_on=(
                        datetime.fromisoformat(
                            item.get("updated_on").replace("Z", "+00:00")
                        )
                        if item.get("updated_on")
                        else None
                    ),
                    parent=(
                        item.get("parent", {}).get("id") if item.get("parent") else None
                    ),
                )
            )

        return comments

    async def create_pull_request_comment(
        self,
        repository: str,
        pr_id: int,
        content: str,
        workspace: str | None = None,
        parent_id: int | None = None,
    ) -> BitbucketComment:
        """Create comment on pull request"""
        workspace = self._get_workspace(workspace)
        endpoint = (
            f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/comments"
        )

        data = {"content": {"raw": content}}

        if parent_id:
            data["parent"] = {"id": str(parent_id)}

        item = await self._request("POST", endpoint, json=data)

        user_data = item.get("user")
        user = None
        if user_data:
            user = BitbucketUser(
                uuid=user_data.get("uuid"),
                username=user_data.get("username"),
                display_name=user_data.get("display_name"),
                account_id=user_data.get("account_id"),
                nickname=user_data.get("nickname"),
            )

        return BitbucketComment(
            id=item.get("id") or 0,
            content=item.get("content", {}),
            user=user,
            created_on=(
                datetime.fromisoformat(
                    item.get("created_on", "").replace("Z", "+00:00")
                )
                if item.get("created_on")
                else None
            ),
            updated_on=(
                datetime.fromisoformat(
                    item.get("updated_on", "").replace("Z", "+00:00")
                )
                if item.get("updated_on")
                else None
            ),
            parent=item.get("parent", {}).get("id") if item.get("parent") else None,
        )

    async def create_pull_request_inline_comment(
        self,
        repository: str,
        pr_id: int,
        content: str,
        filename: str,
        line_number: int,
        workspace: str | None = None,
        parent_id: int | None = None,
    ) -> BitbucketComment:
        """Create inline comment on specific line in pull request diff"""
        workspace = self._get_workspace(workspace)
        endpoint = (
            f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/comments"
        )

        data = {
            "content": {"raw": content},
            "inline": {"to": line_number, "path": filename},
        }

        if parent_id:
            data["parent"] = {"id": str(parent_id)}

        item = await self._request("POST", endpoint, json=data)

        user_data = item.get("user")
        user = None
        if user_data:
            user = BitbucketUser(
                uuid=user_data.get("uuid"),
                username=user_data.get("username"),
                display_name=user_data.get("display_name"),
                account_id=user_data.get("account_id"),
                nickname=user_data.get("nickname"),
            )

        return BitbucketComment(
            id=item.get("id") or 0,
            content=item.get("content", {}),
            user=user,
            created_on=(
                datetime.fromisoformat(
                    item.get("created_on", "").replace("Z", "+00:00")
                )
                if item.get("created_on")
                else None
            ),
            updated_on=(
                datetime.fromisoformat(
                    item.get("updated_on", "").replace("Z", "+00:00")
                )
                if item.get("updated_on")
                else None
            ),
            parent=item.get("parent", {}).get("id") if item.get("parent") else None,
        )

    # Commits
    async def list_commits(
        self,
        repository: str,
        workspace: str | None = None,
        branch: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """List commits in repository"""
        workspace = self._get_workspace(workspace)

        if branch:
            endpoint = f"/repositories/{workspace}/{repository}/commits/{branch}"
        else:
            endpoint = f"/repositories/{workspace}/{repository}/commits"

        params = {"pagelen": limit}
        data = await self._request("GET", endpoint, params=params)

        return list(data.get("values", []))

    async def get_pull_request_diff(
        self,
        repository: str,
        pr_id: int,
        workspace: str | None = None,
        context: int = 3,
    ) -> str:
        """Get pull request diff"""
        workspace = self._get_workspace(workspace)
        endpoint = f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/diff"
        params = {"context": context}

        return await self._request_text("GET", endpoint, params=params)

    async def get_pull_request_diffstat(
        self,
        repository: str,
        pr_id: int,
        workspace: str | None = None,
    ) -> dict[str, Any]:
        """Get pull request diffstat (summary of changes)"""
        workspace = self._get_workspace(workspace)
        endpoint = (
            f"/repositories/{workspace}/{repository}/pullrequests/{pr_id}/diffstat"
        )

        data = await self._request("GET", endpoint)
        return data


# Initialize FastMCP server
mcp = FastMCP(
    name="Bitbucket Cloud MCP",
    instructions="""
    Complete MCP server for Bitbucket Cloud API integration.
    
    Required environment variables:
    - BITBUCKET_USERNAME: Your Bitbucket username
    - BITBUCKET_TOKEN: Your Bitbucket app password  
    - BITBUCKET_DEFAULT_WORKSPACE: Default workspace name
    
    Available tools:
    - list_projects: List projects in workspace
    - list_repositories: List repositories in workspace/project
    - list_commits: List commits in repository
    - list_pull_requests: List pull requests in repository
    - get_pull_request: Get specific pull request details
    - create_pull_request: Create new pull request
    - approve_pull_request: Approve pull request
    - decline_pull_request: Decline pull request
    - merge_pull_request: Merge approved pull request
    - list_pull_request_comments: List comments on pull request
    - create_pull_request_comment: Create comment on pull request
    - create_pull_request_inline_comment: Create inline comment on specific line in pull request diff
    - get_pull_request_diff: Get the diff of a pull request for analysis
    - get_pull_request_diffstat: Get the diffstat (summary of changes) of a pull request
    """,
)


@mcp.tool()
async def list_projects(
    workspace: str | None = None, limit: int = 25, start: int = 0
) -> list[dict[str, Any]]:
    """
    List all Bitbucket projects you have access to.

    Args:
        workspace: Workspace name (optional, uses BITBUCKET_DEFAULT_WORKSPACE if not provided)
        limit: Number of projects to return (default: 25, max: 1000)
        start: Start index for pagination (default: 0)

    Returns:
        List of projects with their details
    """
    logger.info(
        f"Listing projects for workspace: {workspace}, limit: {limit}, start: {start}"
    )

    try:
        async with BitbucketCloudClient() as client:
            projects = await client.list_projects(workspace, limit, start)

            result = []
            for project in projects:
                result.append(
                    {
                        "uuid": project.uuid,
                        "key": project.key,
                        "name": project.name,
                        "description": project.description,
                        "is_private": project.is_private,
                        "created_on": (
                            project.created_on.isoformat()
                            if project.created_on
                            else None
                        ),
                        "updated_on": (
                            project.updated_on.isoformat()
                            if project.updated_on
                            else None
                        ),
                    }
                )

            logger.info(f"Found {len(result)} projects")
            return result

    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise


@mcp.tool()
async def list_repositories(
    workspace: str | None = None,
    project: str | None = None,
    limit: int = 25,
    start: int = 0,
) -> list[dict[str, Any]]:
    """
    List repositories within a workspace or project.

    Args:
        workspace: Workspace name (optional)
        project: Project key to filter repositories (optional)
        limit: Number of repositories to return (default: 25, max: 1000)
        start: Start index for pagination (default: 0)

    Returns:
        List of repositories with their details
    """
    logger.info(f"Listing repositories for workspace: {workspace}, project: {project}")

    try:
        async with BitbucketCloudClient() as client:
            repositories = await client.list_repositories(
                workspace, project, limit, start
            )

            result = []
            for repo in repositories:
                result.append(
                    {
                        "uuid": repo.uuid,
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "description": repo.description,
                        "is_private": repo.is_private,
                        "clone_links": repo.clone_links,
                        "size": repo.size,
                        "language": repo.language,
                        "created_on": (
                            repo.created_on.isoformat() if repo.created_on else None
                        ),
                        "updated_on": (
                            repo.updated_on.isoformat() if repo.updated_on else None
                        ),
                    }
                )

            logger.info(f"Found {len(result)} repositories")
            return result

    except Exception as e:
        logger.error(f"Error listing repositories: {e}")
        raise


@mcp.tool()
async def get_pull_request(
    repository: str, pr_id: int, workspace: str | None = None
) -> dict[str, Any] | None:
    """
    Get details of a specific pull request.

    Args:
        repository: Repository slug containing the pull request
        pr_id: Pull request ID number
        workspace: Workspace name (optional)

    Returns:
        Pull request details or None if not found
    """
    logger.info(f"Getting pull request {pr_id} from {repository}")

    try:
        async with BitbucketCloudClient() as client:
            pr = await client.get_pull_request(repository, pr_id, workspace)

            if not pr:
                logger.warning(f"Pull request {pr_id} not found in {repository}")
                return None

            result = {
                "id": pr.id,
                "title": pr.title,
                "description": pr.description,
                "state": pr.state,
                "author": (
                    {
                        "uuid": pr.author.uuid,
                        "username": pr.author.username,
                        "display_name": pr.author.display_name,
                        "account_id": pr.author.account_id,
                        "nickname": pr.author.nickname,
                    }
                    if pr.author
                    else None
                ),
                "source": {"name": pr.source.name} if pr.source else None,
                "destination": (
                    {"name": pr.destination.name} if pr.destination else None
                ),
                "created_on": pr.created_on.isoformat() if pr.created_on else None,
                "updated_on": pr.updated_on.isoformat() if pr.updated_on else None,
                "close_source_branch": pr.close_source_branch,
                "reviewers": pr.reviewers,
                "participants": pr.participants,
            }

            logger.info(f"Retrieved pull request {pr_id} successfully")
            return result

    except Exception as e:
        logger.error(f"Error getting pull request: {e}")
        raise


@mcp.tool()
async def list_commits(
    repository: str,
    workspace: str | None = None,
    branch: str | None = None,
    limit: int = 25,
) -> list[dict[str, Any]]:
    """
    List commits in repository.

    Args:
        repository: Repository slug
        workspace: Workspace name (optional)
        branch: Branch name to list commits from (optional, defaults to main branch)
        limit: Number of commits to return (default: 25)

    Returns:
        List of commits with their details
    """
    logger.info(f"Listing commits for {repository}, branch: {branch}")

    try:
        async with BitbucketCloudClient() as client:
            commits = await client.list_commits(repository, workspace, branch, limit)

            result = []
            for commit in commits:
                result.append(
                    {
                        "hash": commit.get("hash"),
                        "message": commit.get("message"),
                        "author": (
                            {
                                "user": commit.get("author", {}).get("user", {}),
                                "raw": commit.get("author", {}).get("raw"),
                            }
                            if commit.get("author")
                            else None
                        ),
                        "date": commit.get("date"),
                        "parents": [
                            parent.get("hash") for parent in commit.get("parents", [])
                        ],
                        "links": commit.get("links", {}),
                    }
                )

            logger.info(f"Found {len(result)} commits")
            return result

    except Exception as e:
        logger.error(f"Error listing commits: {e}")
        raise


@mcp.tool()
async def list_pull_requests(
    repository: str, workspace: str | None = None, state: str = "OPEN", limit: int = 25
) -> list[dict[str, Any]]:
    """
    List pull requests in repository.

    Args:
        repository: Repository slug
        workspace: Workspace name (optional)
        state: Pull request state (OPEN, MERGED, DECLINED, SUPERSEDED)
        limit: Number of pull requests to return (default: 25)

    Returns:
        List of pull requests with their details
    """
    logger.info(f"Listing pull requests for {repository}, state: {state}")

    try:
        async with BitbucketCloudClient() as client:
            pull_requests = await client.list_pull_requests(
                repository, workspace, state, limit
            )

            result = []
            for pr in pull_requests:
                result.append(
                    {
                        "id": pr.id,
                        "title": pr.title,
                        "description": pr.description,
                        "state": pr.state,
                        "author": (
                            {
                                "uuid": pr.author.uuid,
                                "username": pr.author.username,
                                "display_name": pr.author.display_name,
                                "account_id": pr.author.account_id,
                                "nickname": pr.author.nickname,
                            }
                            if pr.author
                            else None
                        ),
                        "source": {"name": pr.source.name} if pr.source else None,
                        "destination": (
                            {"name": pr.destination.name} if pr.destination else None
                        ),
                        "created_on": (
                            pr.created_on.isoformat() if pr.created_on else None
                        ),
                        "updated_on": (
                            pr.updated_on.isoformat() if pr.updated_on else None
                        ),
                        "close_source_branch": pr.close_source_branch,
                        "reviewers": pr.reviewers,
                        "participants": pr.participants,
                    }
                )

            logger.info(f"Found {len(result)} pull requests")
            return result

    except Exception as e:
        logger.error(f"Error listing pull requests: {e}")
        raise


@mcp.tool()
async def create_pull_request(
    repository: str,
    title: str,
    source_branch: str,
    target_branch: str = "main",
    description: str = "",
    workspace: str | None = None,
    close_source_branch: bool = False,
    reviewers: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a new pull request.

    Args:
        repository: Repository slug
        title: Pull request title
        source_branch: Source branch name
        target_branch: Target branch name (default: main)
        description: Pull request description (optional)
        workspace: Workspace name (optional)
        close_source_branch: Whether to close source branch after merge (default: False)
        reviewers: List of reviewer UUIDs (optional)

    Returns:
        Created pull request details
    """
    logger.info(
        f"Creating pull request in {repository}: {source_branch} -> {target_branch}"
    )

    try:
        async with BitbucketCloudClient() as client:
            pr = await client.create_pull_request(
                repository,
                title,
                source_branch,
                target_branch,
                description,
                workspace,
                close_source_branch,
                reviewers,
            )

            result = {
                "id": pr.id,
                "title": pr.title,
                "description": pr.description,
                "state": pr.state,
                "author": (
                    {
                        "uuid": pr.author.uuid,
                        "username": pr.author.username,
                        "display_name": pr.author.display_name,
                        "account_id": pr.author.account_id,
                        "nickname": pr.author.nickname,
                    }
                    if pr.author
                    else None
                ),
                "created_on": pr.created_on.isoformat() if pr.created_on else None,
                "updated_on": pr.updated_on.isoformat() if pr.updated_on else None,
            }

            logger.info(f"Created pull request {pr.id} successfully")
            return result

    except Exception as e:
        logger.error(f"Error creating pull request: {e}")
        raise


@mcp.tool()
async def approve_pull_request(
    repository: str, pr_id: int, workspace: str | None = None
) -> dict[str, Any]:
    """
    Approve a pull request.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        workspace: Workspace name (optional)

    Returns:
        Approval result
    """
    logger.info(f"Approving pull request {pr_id} in {repository}")

    try:
        async with BitbucketCloudClient() as client:
            result = await client.approve_pull_request(repository, pr_id, workspace)

            logger.info(f"Approved pull request {pr_id} successfully")
            return result

    except Exception as e:
        logger.error(f"Error approving pull request: {e}")
        raise


@mcp.tool()
async def decline_pull_request(
    repository: str, pr_id: int, workspace: str | None = None
) -> dict[str, Any]:
    """
    Decline a pull request.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        workspace: Workspace name (optional)

    Returns:
        Decline result
    """
    logger.info(f"Declining pull request {pr_id} in {repository}")

    try:
        async with BitbucketCloudClient() as client:
            result = await client.decline_pull_request(repository, pr_id, workspace)

            logger.info(f"Declined pull request {pr_id} successfully")
            return result

    except Exception as e:
        logger.error(f"Error declining pull request: {e}")
        raise


@mcp.tool()
async def merge_pull_request(
    repository: str,
    pr_id: int,
    merge_strategy: str = "merge_commit",
    workspace: str | None = None,
) -> dict[str, Any]:
    """
    Merge an approved pull request.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        merge_strategy: Merge strategy (merge_commit, squash, fast_forward)
        workspace: Workspace name (optional)

    Returns:
        Merge result
    """
    logger.info(
        f"Merging pull request {pr_id} in {repository} with strategy: {merge_strategy}"
    )

    try:
        async with BitbucketCloudClient() as client:
            result = await client.merge_pull_request(
                repository, pr_id, merge_strategy, workspace
            )

            logger.info(f"Merged pull request {pr_id} successfully")
            return result

    except Exception as e:
        logger.error(f"Error merging pull request: {e}")
        raise


@mcp.tool()
async def list_pull_request_comments(
    repository: str, pr_id: int, workspace: str | None = None
) -> list[dict[str, Any]]:
    """
    List comments on a pull request.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        workspace: Workspace name (optional)

    Returns:
        List of comments
    """
    logger.info(f"Listing comments for pull request {pr_id} in {repository}")

    try:
        async with BitbucketCloudClient() as client:
            comments = await client.list_pull_request_comments(
                repository, pr_id, workspace
            )

            result = []
            for comment in comments:
                result.append(
                    {
                        "id": comment.id,
                        "content": comment.content,
                        "user": (
                            {
                                "uuid": comment.user.uuid,
                                "username": comment.user.username,
                                "display_name": comment.user.display_name,
                                "account_id": comment.user.account_id,
                                "nickname": comment.user.nickname,
                            }
                            if comment.user
                            else None
                        ),
                        "created_on": (
                            comment.created_on.isoformat()
                            if comment.created_on
                            else None
                        ),
                        "updated_on": (
                            comment.updated_on.isoformat()
                            if comment.updated_on
                            else None
                        ),
                        "parent": comment.parent,
                    }
                )

            logger.info(f"Found {len(result)} comments")
            return result

    except Exception as e:
        logger.error(f"Error listing comments: {e}")
        raise


@mcp.tool()
async def create_pull_request_comment(
    repository: str,
    pr_id: int,
    content: str,
    workspace: str | None = None,
    parent_id: int | None = None,
) -> dict[str, Any]:
    """
    Create a comment on a pull request.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        content: Comment content
        workspace: Workspace name (optional)
        parent_id: Parent comment ID for replies (optional)

    Returns:
        Created comment details
    """
    logger.info(f"Creating comment on pull request {pr_id} in {repository}")

    try:
        async with BitbucketCloudClient() as client:
            comment = await client.create_pull_request_comment(
                repository, pr_id, content, workspace, parent_id
            )

            result = {
                "id": comment.id,
                "content": comment.content,
                "user": (
                    {
                        "uuid": comment.user.uuid,
                        "username": comment.user.username,
                        "display_name": comment.user.display_name,
                        "account_id": comment.user.account_id,
                        "nickname": comment.user.nickname,
                    }
                    if comment.user
                    else None
                ),
                "created_on": (
                    comment.created_on.isoformat() if comment.created_on else None
                ),
                "updated_on": (
                    comment.updated_on.isoformat() if comment.updated_on else None
                ),
                "parent": comment.parent,
            }

            logger.info(f"Created comment {comment.id} successfully")
            return result

    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise


@mcp.tool()
async def create_pull_request_inline_comment(
    repository: str,
    pr_id: int,
    content: str,
    filename: str,
    line_number: int,
    workspace: str | None = None,
    parent_id: int | None = None,
) -> dict[str, Any]:
    """
    Create an inline comment on a specific line in a pull request diff.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        content: Comment content
        filename: Path to the file in the repository
        line_number: Line number in the file to comment on
        workspace: Workspace name (optional)
        parent_id: Parent comment ID for replies (optional)

    Returns:
        Created inline comment details
    """
    logger.info(
        f"Creating inline comment on pull request {pr_id} in {repository} at {filename}:{line_number}"
    )

    try:
        async with BitbucketCloudClient() as client:
            comment = await client.create_pull_request_inline_comment(
                repository, pr_id, content, filename, line_number, workspace, parent_id
            )

            result = {
                "id": comment.id,
                "content": comment.content,
                "user": (
                    {
                        "uuid": comment.user.uuid,
                        "username": comment.user.username,
                        "display_name": comment.user.display_name,
                        "account_id": comment.user.account_id,
                        "nickname": comment.user.nickname,
                    }
                    if comment.user
                    else None
                ),
                "created_on": (
                    comment.created_on.isoformat() if comment.created_on else None
                ),
                "updated_on": (
                    comment.updated_on.isoformat() if comment.updated_on else None
                ),
                "parent": comment.parent,
            }

            logger.info(
                f"Created inline comment {comment.id} successfully on {filename}:{line_number}"
            )
            return result

    except Exception as e:
        logger.error(f"Error creating inline comment: {e}")
        raise


@mcp.tool()
async def get_pull_request_diff(
    repository: str,
    pr_id: int,
    workspace: str | None = None,
    context: int = 3,
) -> str:
    """
    Get the diff of a pull request.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        workspace: Workspace name (optional)
        context: Number of context lines around changes (default: 3)

    Returns:
        Raw diff text showing all changes in the pull request
    """
    logger.info(f"Getting diff for pull request {pr_id} in {repository}")

    try:
        async with BitbucketCloudClient() as client:
            diff_text = await client.get_pull_request_diff(
                repository, pr_id, workspace, context
            )

            logger.info(f"Retrieved diff for PR {pr_id} ({len(diff_text)} characters)")
            return diff_text

    except Exception as e:
        logger.error(f"Error getting pull request diff: {e}")
        raise


@mcp.tool()
async def get_pull_request_diffstat(
    repository: str,
    pr_id: int,
    workspace: str | None = None,
) -> dict[str, Any]:
    """
    Get the diffstat (summary of changes) of a pull request.

    Args:
        repository: Repository slug
        pr_id: Pull request ID
        workspace: Workspace name (optional)

    Returns:
        Summary of changes including files modified, lines added/removed
    """
    logger.info(f"Getting diffstat for pull request {pr_id} in {repository}")

    try:
        async with BitbucketCloudClient() as client:
            diffstat = await client.get_pull_request_diffstat(
                repository, pr_id, workspace
            )

            # Process the diffstat to make it more readable
            result: dict[str, Any] = {
                "files_changed": len(diffstat.get("values", [])),
                "files": [],
            }

            for file_stat in diffstat.get("values", []):
                file_info = {
                    "type": file_stat.get("type", "modified"),
                    "status": file_stat.get("status", "modified"),
                    "lines_added": file_stat.get("lines_added", 0),
                    "lines_removed": file_stat.get("lines_removed", 0),
                    "old_file": (
                        file_stat.get("old", {}).get("path")
                        if file_stat.get("old")
                        else None
                    ),
                    "new_file": (
                        file_stat.get("new", {}).get("path")
                        if file_stat.get("new")
                        else None
                    ),
                }
                result["files"].append(file_info)

            logger.info(
                f"Retrieved diffstat for PR {pr_id} - {result['files_changed']} files changed"
            )
            return result

    except Exception as e:
        logger.error(f"Error getting pull request diffstat: {e}")
        raise


def main() -> None:
    """Main entry point for the MCP server"""
    logger.info("Starting Bitbucket Cloud MCP Server")
    logger.info("Available tools:")
    logger.info("  - list_projects: List projects in workspace")
    logger.info("  - list_repositories: List repositories in workspace/project")
    logger.info("  - list_commits: List commits in repository")
    logger.info("  - list_pull_requests: List pull requests in repository")
    logger.info("  - get_pull_request: Get specific pull request details")
    logger.info("  - create_pull_request: Create new pull request")
    logger.info("  - approve_pull_request: Approve pull request")
    logger.info("  - decline_pull_request: Decline pull request")
    logger.info("  - merge_pull_request: Merge approved pull request")
    logger.info("  - list_pull_request_comments: List comments on pull request")
    logger.info("  - create_pull_request_comment: Create comment on pull request")
    logger.info(
        "  - create_pull_request_inline_comment: Create inline comment on specific line in pull request diff"
    )
    logger.info("  - get_pull_request_diff: Get pull request diff for analysis")
    logger.info("  - get_pull_request_diffstat: Get pull request diffstat summary")
    logger.info("  - get_pull_request_diff: Get the diff of a pull request")
    logger.info(
        "  - get_pull_request_diffstat: Get the diffstat (summary of changes) of a pull request"
    )

    # Run the server using STDIO transport (default)
    mcp.run()


if __name__ == "__main__":
    main()
