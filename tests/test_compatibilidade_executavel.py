#!/usr/bin/env python3
"""
Testes automatizados para validação da compatibilidade de empacotamento executável (PyInstaller / sys.frozen).
"""

import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import app


def test_resolucao_app_root_script():
    print("[*] 1. Testando resolução de APP_ROOT em modo script Python...")
    with patch.object(sys, "frozen", False, create=True):
        if getattr(sys, "frozen", False):
            root = Path(sys.executable).resolve().parent
        else:
            root = Path(app.__file__).resolve().parent

        assert root == REPO_ROOT, f"APP_ROOT deveria ser a raiz do repositório: {root}"
        print(f"      [✓] Modo Script: APP_ROOT = {root}")


def test_resolucao_app_root_frozen():
    print("[*] 2. Testando resolução de APP_ROOT em modo binário congelado (sys.frozen)...")
    fake_exe = Path("/opt/contagem/bin/ContagemMultidoes.exe")
    with patch.object(sys, "frozen", True, create=True), \
         patch.object(sys, "executable", str(fake_exe)):
        if getattr(sys, "frozen", False):
            root = Path(sys.executable).resolve().parent
        else:
            root = Path(app.__file__).resolve().parent

        assert root == fake_exe.parent, f"APP_ROOT deveria ser o diretório do executável: {root}"
        input_dir = root / "data" / "input"
        output_dir = root / "data" / "ground_truth"
        assert input_dir == Path("/opt/contagem/bin/data/input")
        assert output_dir == Path("/opt/contagem/bin/data/ground_truth")
        print(f"      [✓] Modo Frozen (.exe): APP_ROOT = {root}")
        print(f"      [✓] Pastas relativas: input = {input_dir}, output = {output_dir}")


if __name__ == "__main__":
    test_resolucao_app_root_script()
    test_resolucao_app_root_frozen()
    print("\n[✓ SUCESSO] Compatibilidade com executável (.exe) 100% validada!")
