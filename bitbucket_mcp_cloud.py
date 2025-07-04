#!/usr/bin/env python3
"""
Bitbucket Cloud MCP Server Entry Point
Main entry point for the Bitbucket Cloud MCP server
"""

import sys


def main():
    """Main entry point for the MCP server"""
    # Se executado com --help, mostrar ajuda e sair
    if "--help" in sys.argv or "-h" in sys.argv:
        print(
            """
Bitbucket Cloud MCP Server

Usage:
  bitbucket-mcp-cloud

This is a Model Context Protocol (MCP) server for Bitbucket Cloud API integration.
It should be used with MCP clients like Claude Desktop.

Environment Variables Required:
  BITBUCKET_USERNAME         - Your Bitbucket username
  BITBUCKET_TOKEN           - Your Bitbucket app password  
  BITBUCKET_DEFAULT_WORKSPACE - Default workspace name

Available Tools:
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
  - create_pull_request_inline_comment: Create inline comment on specific line
  - get_pull_request_diff: Get pull request diff for analysis
  - get_pull_request_diffstat: Get pull request diffstat summary

For more information: https://github.com/jhonymiler/Bitbucket-MCP-Cloud
        """
        )
        sys.exit(0)

    from src.server import main as server_main

    server_main()


if __name__ == "__main__":
    main()
