"""
Pydantic models for Bitbucket Cloud API responses
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BitbucketUser(BaseModel):
    """Bitbucket user model"""

    uuid: str | None = None
    username: str | None = None
    display_name: str | None = None
    account_id: str | None = None
    nickname: str | None = None


class BitbucketProject(BaseModel):
    """Bitbucket project model"""

    uuid: str | None = None
    key: str
    name: str
    description: str | None = None
    is_private: bool = False
    created_on: datetime | None = None
    updated_on: datetime | None = None


class BitbucketRepository(BaseModel):
    """Bitbucket repository model"""

    uuid: str | None = None
    name: str
    full_name: str
    description: str | None = None
    is_private: bool = False
    clone_links: list[dict[str, Any]] = Field(default_factory=list)
    size: int | None = None
    language: str | None = None
    created_on: datetime | None = None
    updated_on: datetime | None = None


class BitbucketBranch(BaseModel):
    """Bitbucket branch reference"""

    name: str
    repository: dict[str, Any] | None = None
    commit: dict[str, Any] | None = None


class BitbucketPullRequest(BaseModel):
    """Bitbucket pull request model"""

    id: int
    title: str
    description: str | None = None
    state: str  # OPEN, MERGED, DECLINED, SUPERSEDED
    author: BitbucketUser | None = None
    source: BitbucketBranch | None = None
    destination: BitbucketBranch | None = None
    created_on: datetime | None = None
    updated_on: datetime | None = None
    close_source_branch: bool = False
    reviewers: list[dict[str, Any]] = Field(default_factory=list)
    participants: list[dict[str, Any]] = Field(default_factory=list)


class BitbucketComment(BaseModel):
    """Bitbucket comment model"""

    id: int
    content: dict[str, Any]
    user: BitbucketUser | None = None
    created_on: datetime | None = None
    updated_on: datetime | None = None
    parent: int | None = None
