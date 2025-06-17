"""
Testes unitários para o Bitbucket Cloud MCP Server
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import our modules
from src.models import (
    BitbucketProject,
    BitbucketPullRequest,
    BitbucketRepository,
    BitbucketUser,
)
from src.utils import get_env_var, setup_logger


class TestModels:
    """Testes para modelos Pydantic"""

    def test_bitbucket_user_creation(self):
        """Testa criação de modelo BitbucketUser"""
        user = BitbucketUser(
            uuid="user-uuid",
            username="testuser",
            display_name="Test User",
            account_id="account-123",
            nickname="tester",
        )

        assert user.uuid == "user-uuid"
        assert user.username == "testuser"
        assert user.display_name == "Test User"

    def test_bitbucket_repository_creation(self):
        """Testa criação de modelo BitbucketRepository"""
        repo = BitbucketRepository(
            uuid="repo-uuid",
            name="test-repo",
            full_name="workspace/test-repo",
            description="Test repository",
            is_private=False,
            clone_links=[],
            size=1024,
            language="Python",
        )

        assert repo.name == "test-repo"
        assert repo.full_name == "workspace/test-repo"
        assert repo.is_private is False
        assert repo.language == "Python"

    def test_bitbucket_pull_request_creation(self):
        """Testa criação de modelo BitbucketPullRequest"""
        pr = BitbucketPullRequest(
            id=123, title="Test PR", description="Test description", state="OPEN"
        )

        assert pr.id == 123
        assert pr.title == "Test PR"
        assert pr.state == "OPEN"


class TestUtils:
    """Testes para funções utilitárias"""

    def test_get_env_var_exists(self):
        """Testa obtenção de variável de ambiente existente"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = get_env_var("TEST_VAR")
            assert result == "test_value"

    def test_get_env_var_with_default(self):
        """Testa obtenção de variável com valor padrão"""
        result = get_env_var("NON_EXISTENT_VAR", "default_value")
        assert result == "default_value"

    def test_get_env_var_missing_raises_error(self):
        """Testa erro quando variável não existe e não há padrão"""
        with pytest.raises(
            ValueError, match="Environment variable MISSING_VAR is required"
        ):
            get_env_var("MISSING_VAR")

    def test_setup_logger(self):
        """Testa configuração de logger"""
        logger = setup_logger("test_logger", "DEBUG")
        assert logger.name == "test_logger"
        assert logger.level == 10  # DEBUG level


@pytest.mark.asyncio
class TestBitbucketCloudClient:
    """Testes para cliente da API do Bitbucket"""

    @patch("server.get_env_var")
    def test_client_initialization(self, mock_get_env):
        """Testa inicialização do cliente"""
        from server import BitbucketCloudClient

        mock_get_env.side_effect = ["testuser", "testpass", "testworkspace"]

        client = BitbucketCloudClient()

        assert client.username == "testuser"
        assert client.app_password == "testpass"
        assert client.default_workspace == "testworkspace"
        assert client.base_url == "https://api.bitbucket.org/2.0"

    @patch("server.get_env_var")
    async def test_client_context_manager(self, mock_get_env):
        """Testa uso do cliente como context manager"""
        from server import BitbucketCloudClient

        mock_get_env.side_effect = ["testuser", "testpass", "testworkspace"]

        async with BitbucketCloudClient() as client:
            assert client._client is not None

    @patch("server.get_env_var")
    @patch("httpx.AsyncClient")
    async def test_request_method(self, mock_client_class, mock_get_env):
        """Testa método _request do cliente"""
        from server import BitbucketCloudClient

        # Configure mocks
        mock_get_env.side_effect = ["testuser", "testpass", "testworkspace"]
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Test
        async with BitbucketCloudClient() as client:
            result = await client._request("GET", "/test")

            assert result == {"test": "data"}
            mock_client.request.assert_called_once()

    @patch("server.get_env_var")
    @patch("httpx.AsyncClient")
    async def test_list_projects(self, mock_client_class, mock_get_env):
        """Testa listagem de projetos"""
        from server import BitbucketCloudClient

        # Configure mocks
        mock_get_env.side_effect = ["testuser", "testpass", "testworkspace"]
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "values": [
                {
                    "uuid": "project-uuid",
                    "key": "PROJ",
                    "name": "Test Project",
                    "description": "Test description",
                    "is_private": False,
                    "created_on": "2023-01-01T00:00:00.000000+00:00",
                    "updated_on": "2023-01-02T00:00:00.000000+00:00",
                }
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Test
        async with BitbucketCloudClient() as client:
            projects = await client.list_projects()

            assert len(projects) == 1
            assert projects[0].key == "PROJ"
            assert projects[0].name == "Test Project"


@pytest.mark.asyncio
class TestMCPTools:
    """Testes para ferramentas MCP"""

    @patch("server.BitbucketCloudClient")
    async def test_list_projects_tool(self, mock_client_class):
        """Testa ferramenta list_projects"""
        from server import list_projects

        # Configure mock
        mock_client = AsyncMock()
        mock_project = BitbucketProject(
            uuid="project-uuid",
            key="PROJ",
            name="Test Project",
            description="Test description",
            is_private=False,
        )
        mock_client.list_projects.return_value = [mock_project]
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Test
        result = await list_projects()

        assert len(result) == 1
        assert result[0]["key"] == "PROJ"
        assert result[0]["name"] == "Test Project"

    @patch("server.BitbucketCloudClient")
    async def test_list_repositories_tool(self, mock_client_class):
        """Testa ferramenta list_repositories"""
        from server import list_repositories

        # Configure mock
        mock_client = AsyncMock()
        mock_repo = BitbucketRepository(
            uuid="repo-uuid",
            name="test-repo",
            full_name="workspace/test-repo",
            description="Test repository",
            is_private=False,
            clone_links=[],
            size=1024,
            language="Python",
        )
        mock_client.list_repositories.return_value = [mock_repo]
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Test
        result = await list_repositories()

        assert len(result) == 1
        assert result[0]["name"] == "test-repo"
        assert result[0]["language"] == "Python"


class TestErrorHandling:
    """Testes para tratamento de erros"""

    @patch("server.BitbucketCloudClient")
    async def test_client_http_error(self, mock_client_class):
        """Testa tratamento de erro HTTP"""
        import httpx

        from server import list_projects

        # Configure mock to raise HTTP error
        mock_client = AsyncMock()
        mock_client.list_projects.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=MagicMock()
        )
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Test
        with pytest.raises(httpx.HTTPStatusError):
            await list_projects()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
