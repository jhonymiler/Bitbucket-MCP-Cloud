# Bitbucket Cloud MCP Server

[![PyPI version](https://badge.fury.io/py/bitbucket-mcp-cloud.svg)](https://badge.fury.io/py/bitbucket-mcp-cloud)
[![Python](https://img.shields.io/pypi/pyversions/bitbucket-mcp-cloud.svg)](https://pypi.org/project/bitbucket-mcp-cloud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/jhonymiler/Bitbucket-MCP-Cloud/actions/workflows/publish.yml/badge.svg)](https://github.com/jhonymiler/Bitbucket-MCP-Cloud/actions/workflows/publish.yml)

A complete **Model Context Protocol (MCP)** server for integration with the Bitbucket Cloud API. This project provides programmatic access to all essential Bitbucket Cloud functionalities, including repository management, pull requests, commits, and comments.

## 🚀 Features

### ✅ Implemented (14 tools)

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
- **`create_pull_request_inline_comment`** - Create inline comment on specific line in pull request diff
- **`get_pull_request_diff`** - Get pull request diff for analysis
- **`get_pull_request_diffstat`** - Get pull request diffstat summary

## � Installation

### From PyPI (Recommended)

```bash
pip install bitbucket-mcp-cloud
```

### From Source

```bash
# Clone the repository
git clone https://github.com/jhonymiler/Bitbucket-MCP-Cloud.git
cd Bitbucket-MCP-Cloud

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

## �📋 Prerequisites

- Python 3.10+
- A Bitbucket Cloud account
- Configured Bitbucket App Password

## ⚙️ Setup

### 1. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Configure credentials

1. Create an **App Password** in Bitbucket:
   - Go to: [Account Settings > App Passwords](https://bitbucket.org/account/settings/app-passwords/)
   - Click "Create app password"
   - Select the required permissions:
     - **Repositories**: Read, Write
     - **Pull requests**: Read, Write
     - **Projects**: Read

2. Configure environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
BITBUCKET_USERNAME=your_username
BITBUCKET_TOKEN=your_app_password
BITBUCKET_DEFAULT_WORKSPACE=your_workspace
```

### 3. Run the server

```bash
# Using uv
uv run server.py

# Or directly with Python
python server.py
```

## 🔧 Tool Usage

### Projects

```python
# List projects
await list_projects(workspace="my-workspace", limit=25)
```

### Repositories

```python
# List all repositories
await list_repositories(workspace="my-workspace")

# List repositories for a specific project
await list_repositories(workspace="my-workspace", project="PROJ")
```

### Commits

```python
# List commits from main branch
await list_commits(repository="my-repo")

# List commits from a specific branch
await list_commits(repository="my-repo", branch="feature/new-feature")
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

# Approve PR
await approve_pull_request(repository="my-repo", pr_id=123)

# Merge PR
await merge_pull_request(repository="my-repo", pr_id=123, merge_strategy="squash")
```

### Comments

```python
# List comments on a PR
await list_pull_request_comments(repository="my-repo", pr_id=123)

# Create comment
await create_pull_request_comment(
    repository="my-repo",
    pr_id=123,
    content="Excellent implementation!"
)

# Reply to a comment
await create_pull_request_comment(
    repository="my-repo",
    pr_id=123,
    content="I agree!",
    parent_id=456
)

# Create inline comment on specific line in diff
await create_pull_request_inline_comment(
    repository="my-repo",
    pr_id=123,
    content="This function could be optimized",
    filename="src/main.py",
    line_number=42
)
```

### Diff Analysis

```python
# Get full diff of a pull request
diff_text = await get_pull_request_diff(repository="my-repo", pr_id=123)

# Get diff with more context lines
diff_text = await get_pull_request_diff(
    repository="my-repo", 
    pr_id=123, 
    context=5
)

# Get diffstat summary of changes
diffstat = await get_pull_request_diffstat(repository="my-repo", pr_id=123)
print(f"Files changed: {diffstat['files_changed']}")
for file in diffstat['files']:
    print(f"{file['new_file']}: +{file['lines_added']} -{file['lines_removed']}")
```

## 🏗️ Architecture

```
bitbucket-mcp-cloud/
├── server.py              # Main MCP server
├── src/
│   ├── models.py          # Pydantic models
│   ├── utils.py           # Utility functions
│   └── __init__.py
├── tests/                 # Automated tests
├── pyproject.toml         # Project configuration
├── .env.example          # Configuration example
└── README.md             # Documentation
```

### Main Components

- **`BitbucketCloudClient`**: Complete HTTP client for Bitbucket API
- **`FastMCP`**: MCP server with all registered tools
- **Pydantic Models**: Data validation and serialization
- **Logging System**: Detailed operation tracking

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific tests
uv run pytest tests/test_client.py -v
```

## 🔒 Security

- **Secure authentication** using Bitbucket App Passwords
- **Input validation** with Pydantic
- **Robust error handling** in all operations
- **Detailed logging** for auditing and debugging

## 📚 API Documentation

This MCP uses the [official Bitbucket Cloud REST API](https://developer.atlassian.com/cloud/bitbucket/rest/intro/). Consult the official documentation for details about:

- Rate limiting
- Response formats
- Error codes
- Webhooks and integrations

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Useful Links

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Bitbucket Cloud API](https://developer.atlassian.com/cloud/bitbucket/rest/intro/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Bitbucket App Passwords](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/)
