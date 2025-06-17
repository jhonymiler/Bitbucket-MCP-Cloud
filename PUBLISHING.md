# 📦 Guia de Publicação

Este guia mostra como publicar o Bitbucket Cloud MCP Server no PyPI e no ecossistema FastMCP/MCP.

## 🔗 PyPI (Python Package Index)

### 1. Preparação

#### Configurar Trusted Publishing no PyPI

1. **Acesse o PyPI**: https://pypi.org/manage/account/publishing/
2. **Configure o Trusted Publisher**:
   - Project name: `bitbucket-mcp-cloud`
   - Owner: `jhonymiler`
   - Repository: `Bitbucket-MCP-Cloud`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`

3. **Acesse o TestPyPI**: https://test.pypi.org/manage/account/publishing/
4. **Repita a configuração** com Environment name: `testpypi`

#### Configurar Environments no GitHub

1. **Acesse**: https://github.com/jhonymiler/Bitbucket-MCP-Cloud/settings/environments
2. **Crie dois environments**:
   - `pypi` (para produção)
   - `testpypi` (para testes)

### 2. Publicação Automática

#### Via GitHub Actions (Recomendado)

```bash
# 1. Certifique-se que todos os testes passam
uv run pytest

# 2. Crie uma tag de versão
git tag v1.0.0
git push origin v1.0.0

# 3. O GitHub Actions irá automaticamente:
#    - Executar testes
#    - Buildar o pacote
#    - Publicar no TestPyPI
#    - Publicar no PyPI
```

#### Publicação Manual

```bash
# 1. Instalar dependências de build
pip install build twine

# 2. Limpar builds anteriores
rm -rf dist/ build/ *.egg-info/

# 3. Buildar o pacote
python -m build

# 4. Verificar o pacote
twine check dist/*

# 5. Publicar no TestPyPI (teste)
twine upload --repository testpypi dist/*

# 6. Testar a instalação
pip install --index-url https://test.pypi.org/simple/ bitbucket-mcp-cloud

# 7. Publicar no PyPI (produção)
twine upload dist/*
```

### 3. Verificação da Publicação

```bash
# Instalar do PyPI
pip install bitbucket-mcp-cloud

# Verificar instalação
python -c "import server; print('✅ Instalação OK')"

# Testar o servidor
bitbucket-mcp-server --help
```

## 🚀 FastMCP / MCP Ecosystem

### 1. Submissão para o MCP Server Registry

#### Repositório Oficial
- **URL**: https://github.com/modelcontextprotocol/servers
- **Processo**: Abrir Pull Request adicionando o servidor à lista

#### Passos para submissão:

1. **Fork do repositório**: https://github.com/modelcontextprotocol/servers
2. **Editar** o arquivo `README.md`
3. **Adicionar** na seção apropriada:

```markdown
* **[Bitbucket Cloud](https://github.com/jhonymiler/Bitbucket-MCP-Cloud)** - Complete Bitbucket Cloud API integration with repository management, pull requests, commits, and comments
```

4. **Criar Pull Request** com:
   - Título: `Add Bitbucket Cloud MCP Server`
   - Descrição: Detalhes do servidor e funcionalidades

### 2. FastMCP Marketplace

#### Submissão ao FastMCP
- **URL**: https://gofastmcp.com/mcp-servers/
- **Processo**: Atualmente em desenvolvimento, seguir documentação oficial

### 3. Documentação e Metadata

#### Adicionar badges ao README.md

```markdown
[![PyPI version](https://badge.fury.io/py/bitbucket-mcp-cloud.svg)](https://badge.fury.io/py/bitbucket-mcp-cloud)
[![Python](https://img.shields.io/pypi/pyversions/bitbucket-mcp-cloud.svg)](https://pypi.org/project/bitbucket-mcp-cloud/)
[![Downloads](https://pepy.tech/badge/bitbucket-mcp-cloud)](https://pepy.tech/project/bitbucket-mcp-cloud)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

#### Criar arquivo MANIFEST.in (se necessário)

```text
include README.md
include LICENSE
include .env.example
recursive-include src *.py
recursive-include tests *.py
```

## 📊 Monitoramento

### PyPI Analytics
- **URL**: https://pypi.org/project/bitbucket-mcp-cloud/
- **Downloads**: Acompanhar via https://pepy.tech/

### GitHub Releases
- **Criar releases**: Para cada versão publicada
- **Changelog**: Documentar mudanças importantes

## 🔄 Processo de Atualização

### Versionamento (Semantic Versioning)

```bash
# Patch (bugfixes): 1.0.0 -> 1.0.1
# Minor (novas features): 1.0.0 -> 1.1.0  
# Major (breaking changes): 1.0.0 -> 2.0.0
```

### Workflow de Atualização

1. **Atualizar versão** no `pyproject.toml`
2. **Commitar mudanças**
3. **Criar tag**: `git tag v1.0.1`
4. **Push**: `git push origin v1.0.1`
5. **GitHub Actions** irá automaticamente publicar

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Erro de permissões**: Verificar configuração do Trusted Publishing
2. **Conflito de versão**: Verificar se a versão já existe no PyPI
3. **Build falha**: Verificar dependências e estrutura do projeto
4. **Testes falham**: Corrigir antes de publicar

### Logs e Debug

```bash
# Ver logs do build
python -m build --verbose

# Validar metadados
python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb')))"

# Testar import local
python -c "import sys; sys.path.insert(0, 'src'); import server; print('OK')"
```

## 📚 Recursos Úteis

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com/)
