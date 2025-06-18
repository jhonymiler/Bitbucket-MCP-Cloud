# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-06-18

### Added
- **`get_pull_request_diff`** - Get the complete diff of a pull request for code analysis
- **`get_pull_request_diffstat`** - Get diffstat summary showing files changed and lines added/removed
- Support for diff analysis workflows with context line configuration
- Enhanced pull request review capabilities with diff inspection

### Enhanced
- Improved pull request workflow with diff analysis tools
- Better code review experience with inline comment placement guidance

## [1.1.0] - 2025-06-18

### Added
- **`create_pull_request_inline_comment`** - Create inline comments on specific lines in pull request diffs
- Enhanced comment system with line-specific feedback capabilities
- Support for targeted code review comments

### Enhanced
- Extended commenting functionality beyond general PR comments
- Improved code review workflow with precise line-level feedback

## [1.0.0] - 2025-06-18

### Added
- Initial release with complete Bitbucket Cloud MCP server
- **`list_projects`** - List projects in workspace
- **`list_repositories`** - List repositories in workspace/project
- **`list_commits`** - List commits in repository
- **`list_pull_requests`** - List pull requests in repository
- **`get_pull_request`** - Get specific pull request details
- **`create_pull_request`** - Create new pull request
- **`approve_pull_request`** - Approve pull request
- **`decline_pull_request`** - Decline pull request
- **`merge_pull_request`** - Merge approved pull request
- **`list_pull_request_comments`** - List comments on pull request
- **`create_pull_request_comment`** - Create comment on pull request
- Complete authentication system with Bitbucket Cloud API
- Comprehensive error handling and logging
- Full test suite with unit tests
- Professional documentation and examples

### Features
- Model Context Protocol (MCP) server implementation using FastMCP
- Secure authentication with Bitbucket App Passwords
- Complete pull request lifecycle management
- Repository and project management
- Commit tracking and history
- Comment system for collaboration
- Robust error handling and validation
- Comprehensive logging for debugging
- Modular and extensible architecture
