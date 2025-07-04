# Bitbucket Cloud MCP Server

[![PyPI version](https://badge.fury.io/py/bitbucket-mcp-cloud.svg)](https://badge.fury.io/py/bitbucket-mcp-cloud)
[![Python](https://img.shields.io/pypi/pyversions/bitbucket-mcp-cloud.svg)](https://pypi.org/project/bitbucket-mcp-cloud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/jhonymiler/Bitbucket-MCP-Cloud/actions/workflows/publish.yml/badge.svg)](https://github.com/jhonymiler/Bitbucket-MCP-Cloud/actions/workflows/publish.yml)

A **production-ready Model Context Protocol (MCP)** server for seamless integration with the Bitbucket Cloud API. Built with enterprise-grade quality standards, this server provides comprehensive access to Bitbucket Cloud's functionalities through a standardized MCP interface.

## 🌟 Highlights

- ✅ **Complete Bitbucket Cloud API Coverage** - All essential features implemented
- ✅ **Production Ready** - Comprehensive error handling, logging, and type safety
- ✅ **Multiple Installation Methods** - PyPI, direct execution, or development mode
- ✅ **Claude Desktop Integration** - Ready for AI assistant workflows
- ✅ **Fully Tested** - Comprehensive test suite with automated CI/CD
- ✅ **Clean Architecture** - Modular design following SOLID principles

## 🛠️ Features (14 Tools)

### 🎯 Project & Repository Management
- **`list_projects`** - List all accessible projects in workspace
- **`list_repositories`** - List repositories by workspace or project
- **`list_commits`** - Browse commit history with filtering options

### 🔄 Pull Request Lifecycle
- **`list_pull_requests`** - List PRs with state filtering (OPEN, MERGED, DECLINED)
- **`get_pull_request`** - Get detailed PR information
- **`create_pull_request`** - Create new pull requests with reviewers
- **`approve_pull_request`** - Approve pull requests
- **`decline_pull_request`** - Decline pull requests
- **`merge_pull_request`** - Merge approved PRs with strategy selection

### 💬 Comment System
- **`list_pull_request_comments`** - List all PR comments
- **`create_pull_request_comment`** - Add general comments
- **`create_pull_request_inline_comment`** - Add line-specific code comments

### 📊 Code Analysis
- **`get_pull_request_diff`** - Get full diff for code review
- **`get_pull_request_diffstat`** - Get summary of changes (files, lines added/removed)

## 🚀 Installation & Usage

### Method 1: Direct Execution via uvx (Recommended)

```bash
# No installation needed - run directly from PyPI
uvx bitbucket-mcp-cloud

# For MCP tools that support it
mcp run bitbucket-mcp-cloud
```

### Method 2: Global Installation

```bash
# Install globally
pip install bitbucket-mcp-cloud

# Run the server
bitbucket-mcp-cloud
```

### Method 3: Development Mode

```bash
# Clone and setup for development
git clone https://github.com/jhonymiler/Bitbucket-MCP-Cloud.git
cd Bitbucket-MCP-Cloud

# Using uv (recommended)
uv sync
uv run server.py

# Or using pip
pip install -e .
python server.py
```

### Method 4: MCP Tools Integration

```bash
# Using the MCP CLI
mcp run server.py

# For development and testing
uv run mcp dev server.py
```

## 📋 Prerequisites

- Python 3.10+
- A Bitbucket Cloud account
- Configured Bitbucket App Password

## ⚙️ Setup

### 1. Create Bitbucket App Password

1. Go to: [Account Settings > App Passwords](https://bitbucket.org/account/settings/app-passwords/)
2. Click "Create app password"
3. Select the required permissions:
   - **Repositories**: Read, Write
   - **Pull requests**: Read, Write
   - **Projects**: Read

### 2. Configure Environment Variables

```bash
# Option 1: Using .env file (for development)
cp .env.example .env
# Edit .env with your credentials

# Option 2: Export environment variables
export BITBUCKET_USERNAME=your_username
export BITBUCKET_TOKEN=your_app_password
export BITBUCKET_DEFAULT_WORKSPACE=your_workspace
```

### 3. Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bitbucket": {
      "command": "uvx",
      "args": ["bitbucket-mcp-cloud"],
      "env": {
        "BITBUCKET_USERNAME": "your_username",
        "BITBUCKET_TOKEN": "your_app_password",
        "BITBUCKET_DEFAULT_WORKSPACE": "your_workspace"
      }
    }
  }
}
```

## 🔧 Tool Usage Examples

### Projects and Repositories

```python
# List projects
await list_projects(workspace="my-workspace", limit=25)

# List all repositories
await list_repositories(workspace="my-workspace")

# List repositories for a specific project
await list_repositories(workspace="my-workspace", project="PROJ")
```

### Pull Requests

```python
# List open PRs
await list_pull_requests(repository="my-repo", state="OPEN")

# Get PR details
await get_pull_request(repository="my-repo", pr_id=123)

# Create new PR
await create_pull_request(
    repository="my-repo",
    title="New feature",
    source_branch="feature/new-feature",
    target_branch="main",
    description="Implements new feature X"
)

# Approve and merge PR
await approve_pull_request(repository="my-repo", pr_id=123)
await merge_pull_request(repository="my-repo", pr_id=123, merge_strategy="squash")
```

### Comments and Code Review

```python
# Create inline comment on specific line
await create_pull_request_inline_comment(
    repository="my-repo",
    pr_id=123,
    content="This function could be optimized",
    filename="src/main.py",
    line_number=42
)

# Get diff for analysis
diff_text = await get_pull_request_diff(repository="my-repo", pr_id=123)

# Get summary of changes
diffstat = await get_pull_request_diffstat(repository="my-repo", pr_id=123)
```

## 🏗️ Architecture

```
bitbucket-mcp-cloud/
├── server.py              # Main MCP server (entry point)
├── src/
│   ├── models.py          # Pydantic models for type safety
│   ├── utils.py           # Utility functions and logging
│   └── __init__.py
├── tests/                 # Comprehensive test suite
│   └── test_bitbucket_mcp.py
├── pyproject.toml         # Project configuration
├── .env.example          # Configuration template
├── .github/
│   └── workflows/
│       └── publish.yml   # CI/CD pipeline
└── README.md             # This documentation
```

### Key Components

- **`BitbucketCloudClient`**: Async HTTP client with comprehensive API coverage
- **`FastMCP`**: MCP server with auto-generated tool definitions
- **Pydantic Models**: Type-safe data structures for all API responses
- **Comprehensive Logging**: Detailed operation tracking and debugging
- **Error Handling**: Robust error handling with proper HTTP status codes

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test categories
uv run pytest tests/test_bitbucket_mcp.py::TestMCPTools -v

# Type checking
uv run mypy server.py src/

# Code formatting
uv run black server.py src/ tests/
```

## 🔒 Security Features

- **Secure Authentication**: Uses Bitbucket App Passwords (no OAuth complexity)
- **Input Validation**: Comprehensive validation using Pydantic models
- **Error Handling**: Sanitized error messages (no credential leakage)
- **Rate Limiting Awareness**: Respects Bitbucket API rate limits
- **HTTPS Only**: All communications encrypted

## 📊 Quality Assurance

- **Type Safety**: Full type annotations with mypy validation
- **Code Quality**: Black formatting and comprehensive linting
- **Testing**: 17 test cases covering all major functionality
- **CI/CD**: Automated testing and PyPI publishing
- **Documentation**: Comprehensive docstrings and examples

## 🔗 API Reference

This MCP server implements the complete [Bitbucket Cloud REST API v2.0](https://developer.atlassian.com/cloud/bitbucket/rest/intro/). Key API endpoints covered:

- `/workspaces/{workspace}/projects` - Project management
- `/repositories/{workspace}` - Repository operations
- `/repositories/{workspace}/{repo}/pullrequests` - PR lifecycle
- `/repositories/{workspace}/{repo}/commits` - Commit history
- `/pullrequests/{pr_id}/comments` - Comment system
- `/pullrequests/{pr_id}/diff` - Code analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`uv run pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/jhonymiler/Bitbucket-MCP-Cloud.git
cd Bitbucket-MCP-Cloud
uv sync --extra dev

# Run quality checks
uv run pytest
uv run mypy server.py src/
uv run black --check server.py src/ tests/
```

## 📝 Changelog

### v1.3.5 (Latest)
- ✅ Package restructured for optimal PyPI distribution
- ✅ Server.py in root with conditional imports
- ✅ All execution methods tested and working
- ✅ Enhanced build system and CI/CD
- ✅ Production-ready package structure

### v1.3.4
- ✅ Server correctly included in PyPI wheel
- ✅ All execution methods working (uvx, pip, development)
- ✅ Complete test coverage
- ✅ Claude Desktop integration ready

### v1.3.x Series
- ✅ Complete Bitbucket Cloud API implementation
- ✅ Comprehensive error handling and logging
- ✅ Type safety with mypy validation
- ✅ Production-ready architecture

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/jhonymiler/Bitbucket-MCP-Cloud/issues)
- **Documentation**: This README and inline code documentation
- **API Reference**: [Bitbucket Cloud REST API](https://developer.atlassian.com/cloud/bitbucket/rest/intro/)

## 🔗 Related Links

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/download)
- [Bitbucket App Passwords Guide](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/)
- [uv Python Package Manager](https://docs.astral.sh/uv/)

---

**Made with ❤️ for the MCP community**
