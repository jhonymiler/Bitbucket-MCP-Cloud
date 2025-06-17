# 📋 Checklist de Publicação

Use este checklist para garantir que tudo está pronto antes de publicar.

## ✅ Pré-publicação

### Código e Testes
- [ ] Todos os testes passam (`uv run pytest`)
- [ ] Linting OK (`uv run ruff check`)
- [ ] Formatação OK (`uv run black --check .`)
- [ ] Type checking OK (`uv run mypy src`)
- [ ] Cobertura de testes adequada

### Documentação
- [ ] README.md atualizado
- [ ] Changelog atualizado
- [ ] Versão atualizada no `pyproject.toml`
- [ ] Docstrings atualizadas
- [ ] Exemplos funcionando

### Configuração
- [ ] `pyproject.toml` configurado corretamente
- [ ] `.env.example` atualizado
- [ ] `requirements.txt` ou dependências no `pyproject.toml`
- [ ] `.gitignore` configurado

## 🔧 Configuração PyPI

### Conta e Credenciais
- [ ] Conta no PyPI criada
- [ ] Conta no TestPyPI criada
- [ ] Trusted Publishing configurado no PyPI
- [ ] Trusted Publishing configurado no TestPyPI

### GitHub
- [ ] Environments `pypi` e `testpypi` criados
- [ ] GitHub Actions configurado (`publish.yml`)
- [ ] Repositório público no GitHub

## 📦 Publicação

### Método 1: GitHub Actions (Recomendado)
- [ ] Criar tag: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Verificar build no GitHub Actions
- [ ] Verificar publicação no TestPyPI
- [ ] Verificar publicação no PyPI

### Método 2: Script Automatizado
```bash
# Publicar nova versão
python scripts/publish.py --version 1.0.1

# Apenas TestPyPI (para testes)
python scripts/publish.py --testpypi-only

# Apenas PyPI (se TestPyPI já foi testado)
python scripts/publish.py --pypi-only
```

### Método 3: Manual
- [ ] Build: `python -m build`
- [ ] Check: `twine check dist/*`
- [ ] TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Test install: `pip install --index-url https://test.pypi.org/simple/ bitbucket-mcp-cloud`
- [ ] PyPI: `twine upload dist/*`

## 🧪 Pós-publicação

### Verificação
- [ ] Instalar do PyPI: `pip install bitbucket-mcp-cloud`
- [ ] Testar import: `python -c "import server; print('OK')"`
- [ ] Testar CLI: `bitbucket-mcp-server --help`
- [ ] Verificar badges no README
- [ ] Verificar página do PyPI

### Release GitHub
- [ ] Criar release no GitHub
- [ ] Adicionar changelog do release
- [ ] Anexar arquivos de distribuição

## 🌟 MCP Ecosystem

### Submissão MCP Registry
- [ ] Fork: https://github.com/modelcontextprotocol/servers
- [ ] Adicionar ao README.md do registry
- [ ] Criar Pull Request
- [ ] Aguardar aprovação

### FastMCP Marketplace
- [ ] Verificar processo atual em https://gofastmcp.com/
- [ ] Submeter conforme instruções
- [ ] Aguardar aprovação

## 📊 Monitoramento

### Métricas
- [ ] Configurar monitoring de downloads
- [ ] Verificar analytics do GitHub
- [ ] Acompanhar feedback da comunidade

### Manutenção
- [ ] Planejar próximas versões
- [ ] Responder issues e PRs
- [ ] Atualizar dependências regularmente

## 🔄 Versionamento

### Semantic Versioning
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, correções menores
- **MINOR** (1.0.0 → 1.1.0): Novas funcionalidades, compatível
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes, incompatível

### Processo de Release
1. Atualizar versão no `pyproject.toml`
2. Atualizar `CHANGELOG.md`
3. Commitar: `git commit -m "Bump version to X.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push origin vX.Y.Z`
6. GitHub Actions fará o resto automaticamente

## 🆘 Troubleshooting

### Problemas Comuns
- **Erro 403**: Verificar Trusted Publishing
- **Versão já existe**: Incrementar versão
- **Build falha**: Verificar dependências
- **Import falha**: Verificar estrutura de pastas

### Debug
```bash
# Verificar build local
python -c "import sys; sys.path.insert(0, 'src'); import server; print('OK')"

# Testar distribuição
pip install dist/*.whl
python -c "import server; print('OK')"

# Logs detalhados
python -m build --verbose
```
