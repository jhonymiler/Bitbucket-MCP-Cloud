#!/usr/bin/env python3
"""
Script para automatizar a publicação do Bitbucket Cloud MCP Server.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Executa um comando e retorna o resultado."""
    print(f"🔄 Executando: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"❌ Erro ao executar: {cmd}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        sys.exit(1)

    return result


def get_current_version() -> str:
    """Obtém a versão atual do pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        content = f.read()

    # Busca a linha version = "x.y.z"
    match = re.search(r'version = "([^"]+)"', content)
    if match:
        return match.group(1)

    raise ValueError("Versão não encontrada no pyproject.toml")


def validate_version(version: str) -> bool:
    """Valida se a versão segue o padrão semântico."""
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def update_version(new_version: str):
    """Atualiza a versão no pyproject.toml."""
    with open("pyproject.toml") as f:
        content = f.read()

    # Substitui a versão
    pattern = r'version = "[^"]+"'
    replacement = f'version = "{new_version}"'
    new_content = re.sub(pattern, replacement, content)

    with open("pyproject.toml", "w") as f:
        f.write(new_content)

    print(f"✅ Versão atualizada para {new_version}")


def run_tests():
    """Executa todos os testes."""
    print("🧪 Executando testes...")
    run_command("uv run pytest")
    print("✅ Testes passaram")


def run_linting():
    """Executa linting e formatação."""
    print("🔍 Executando linting...")
    run_command("uv run black --check .")
    run_command("uv run mypy src")
    print("✅ Linting passou")


def build_package():
    """Builda o pacote."""
    print("📦 Buildando pacote...")

    # Limpa builds anteriores
    run_command("rm -rf dist/ build/ *.egg-info/", check=False)

    # Instala dependências de build
    run_command("pip install build twine")

    # Builda
    run_command("python -m build")

    # Verifica
    run_command("twine check dist/*")

    print("✅ Pacote buildado e verificado")


def publish_to_testpypi():
    """Publica no TestPyPI."""
    print("🚀 Publicando no TestPyPI...")
    run_command("twine upload --repository testpypi dist/*")
    print("✅ Publicado no TestPyPI")


def publish_to_pypi():
    """Publica no PyPI."""
    print("🚀 Publicando no PyPI...")
    run_command("twine upload dist/*")
    print("✅ Publicado no PyPI")


def create_git_tag(version: str):
    """Cria tag no Git."""
    print(f"🏷️ Criando tag v{version}...")
    run_command("git add .")
    run_command(f'git commit -m "Bump version to {version}"')
    run_command(f"git tag v{version}")
    run_command(f"git push origin v{version}")
    run_command("git push")
    print(f"✅ Tag v{version} criada e enviada")


def main():
    parser = argparse.ArgumentParser(description="Publica o Bitbucket Cloud MCP Server")
    parser.add_argument("--version", help="Nova versão (ex: 1.0.1)")
    parser.add_argument("--skip-tests", action="store_true", help="Pula testes")
    parser.add_argument("--skip-lint", action="store_true", help="Pula linting")
    parser.add_argument(
        "--testpypi-only", action="store_true", help="Publica apenas no TestPyPI"
    )
    parser.add_argument(
        "--pypi-only", action="store_true", help="Publica apenas no PyPI"
    )
    parser.add_argument("--no-tag", action="store_true", help="Não cria tag Git")

    args = parser.parse_args()

    # Verifica se está no diretório correto
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml não encontrado. Execute no diretório raiz do projeto.")
        sys.exit(1)

    current_version = get_current_version()
    print(f"📍 Versão atual: {current_version}")

    # Atualiza versão se especificada
    if args.version:
        if not validate_version(args.version):
            print("❌ Versão deve seguir o padrão semântico (ex: 1.0.1)")
            sys.exit(1)

        update_version(args.version)
        version = args.version
    else:
        version = current_version

    # Executa testes
    if not args.skip_tests:
        run_tests()

    # Executa linting
    if not args.skip_lint:
        run_linting()

    # Builda pacote
    build_package()

    # Publica
    if args.testpypi_only:
        publish_to_testpypi()
    elif args.pypi_only:
        publish_to_pypi()
    else:
        # Publica primeiro no TestPyPI, depois no PyPI
        publish_to_testpypi()

        confirm = input("🤔 TestPyPI OK. Publicar no PyPI? (y/N): ")
        if confirm.lower() == "y":
            publish_to_pypi()
        else:
            print("⏸️ Publicação no PyPI cancelada")
            return

    # Cria tag Git
    if not args.no_tag and args.version:
        confirm = input("🤔 Criar tag Git? (y/N): ")
        if confirm.lower() == "y":
            create_git_tag(version)

    print(f"🎉 Publicação completa! Versão {version}")
    print(f"📦 PyPI: https://pypi.org/project/bitbucket-mcp-cloud/{version}/")


if __name__ == "__main__":
    main()
