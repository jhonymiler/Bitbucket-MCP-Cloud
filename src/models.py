"""
Pydantic models for Bitbucket Cloud API responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BitbucketUser(BaseModel):
    """Bitbucket user model"""
    uuid: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    account_id: Optional[str] = None
    nickname: Optional[str] = None


class BitbucketProject(BaseModel):
    """Bitbucket project model"""
    uuid: Optional[str] = None
    key: str
    name: str
    description: Optional[str] = None
    is_private: bool = False
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None


class BitbucketRepository(BaseModel):
    """Bitbucket repository model"""
    uuid: Optional[str] = None
    name: str
    full_name: str
    description: Optional[str] = None
    is_private: bool = False
    clone_links: List[Dict[str, Any]] = Field(default_factory=list)
    size: Optional[int] = None
    language: Optional[str] = None
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None


class BitbucketBranch(BaseModel):
    """Bitbucket branch reference"""
    name: str
    repository: Optional[Dict[str, Any]] = None
    commit: Optional[Dict[str, Any]] = None


class BitbucketPullRequest(BaseModel):
    """Bitbucket pull request model"""
    id: int
    title: str
    description: Optional[str] = None
    state: str  # OPEN, MERGED, DECLINED, SUPERSEDED
    author: Optional[BitbucketUser] = None
    source: Optional[BitbucketBranch] = None
    destination: Optional[BitbucketBranch] = None
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None
    close_source_branch: bool = False
    reviewers: List[Dict[str, Any]] = Field(default_factory=list)
    participants: List[Dict[str, Any]] = Field(default_factory=list)


class BitbucketComment(BaseModel):
    """Bitbucket comment model"""
    id: int
    content: Dict[str, Any]
    user: Optional[BitbucketUser] = None
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None
    parent: Optional[int] = None
