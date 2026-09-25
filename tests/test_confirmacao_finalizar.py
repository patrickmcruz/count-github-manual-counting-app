#!/usr/bin/env python3
"""
Testes automatizados para a Fase 08:
Validação dos fluxos de confirmação de finalização e rastreamento de alterações pendentes.
"""

import sys
import shutil
from pathlib import Path

# Adiciona raiz do app ao path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import cv2

# Importa o módulo app
import app


def test_rastreamento_alteracoes_e_modal():
    print("[*] Iniciando teste do modal de confirmação e rastreamento de alterações pendentes...")

    # Configura ambiente sintético
    pasta_tmp = Path("data/ground_truth/TEST_MODAL_CENA")
    pasta_tmp.mkdir(parents=True, exist_ok=True)

    app.screen_w = 1280
    app.screen_h = 720
    app.caminho_saida_ativo = pasta_tmp
    app.caminho_img_ativo = Path("data/input/DJI_TEST_FAKE.JPG")
    app.img_base = np.zeros((1000, 1000, 3), dtype=np.uint8)
    app.coordenadas = []
    app.alteracoes_pendentes = False
    app.modal_confirmacao_ativo = False
    app.salvar_ao_finalizar = True
    app.deve_encerrar = False

    # 1. Adicionar ponto deve marcar alteracoes_pendentes = True
    print("  [+] Testando adição de ponto...")
    app.coordenadas.append({"id": 1, "x": 100, "y": 100})
    app.alteracoes_pendentes = True
    assert app.alteracoes_pendentes is True, "alteracoes_pendentes deveria ser True após adicionar ponto"

    # 2. Renderização do modal com alterações pendentes (deve gerar 3 botões)
    print("  [+] Testando renderização do modal com alterações pendentes...")
    test_canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
    app.desenhar_modal_confirmacao(test_canvas)

    assert app.BTN_MODAL_CONFIRMAR_SALVAR != (0, 0, 0, 0), "Botão Confirmar Salvar deve estar configurado"
    assert app.BTN_MODAL_SAIR_SEM_SALVAR != (0, 0, 0, 0), "Botão Sair sem Salvar deve estar presente com alterações pendentes"
    assert app.BTN_MODAL_CANCELAR != (0, 0, 0, 0), "Botão Cancelar deve estar configurado"
    print(f"      Botões gerados (3 opções): Salvar={app.BTN_MODAL_CONFIRMAR_SALVAR}, Descartar={app.BTN_MODAL_SAIR_SEM_SALVAR}, Cancelar={app.BTN_MODAL_CANCELAR}")

    # 3. Salvar checkpoint deve limpar alteracoes_pendentes
    print("  [+] Testando salvar_checkpoint() e limpeza de alterações pendentes...")
    app.salvar_checkpoint(silencioso=True)
    assert app.alteracoes_pendentes is False, "alteracoes_pendentes deveria ser False após salvar_checkpoint"

    # 4. Renderização do modal com tudo salvo (deve gerar 2 botões)
    print("  [+] Testando renderização do modal com tudo salvo...")
    app.desenhar_modal_confirmacao(test_canvas)
    assert app.BTN_MODAL_CONFIRMAR_SALVAR != (0, 0, 0, 0), "Botão Confirmar Salvar deve estar configurado"
    assert app.BTN_MODAL_SAIR_SEM_SALVAR == (0, 0, 0, 0), "Botão Sair sem Salvar NÃO deve estar ativo quando tudo estiver salvo"
    assert app.BTN_MODAL_CANCELAR != (0, 0, 0, 0), "Botão Cancelar deve estar configurado"
    print(f"      Botões gerados (2 opções): Confirmar={app.BTN_MODAL_CONFIRMAR_SALVAR}, Cancelar={app.BTN_MODAL_CANCELAR}")

    # 5. Desfazer ponto deve reativar alteracoes_pendentes
    print("  [+] Testando desfazer_ultimo_ponto()...")
    app.desfazer_ultimo_ponto()
    assert len(app.coordenadas) == 0, "Lista de coordenadas deveria estar vazia após desfazer"
    assert app.alteracoes_pendentes is True, "alteracoes_pendentes deveria ser True após desfazer ponto"

    # 6. Testar fluxo abrir / cancelar modal
    print("  [+] Testando abrir_modal_finalizacao() e cancelar_modal()...")
    app.abrir_modal_finalizacao()
    assert app.modal_confirmacao_ativo is True, "Modal deveria estar ativo"
    app.cancelar_modal()
    assert app.modal_confirmacao_ativo is False, "Modal deveria ser desativado após cancelar"

    # 7. Testar fechar_modal_e_finalizar com salvar=False
    print("  [+] Testando fechar_modal_e_finalizar(salvar=False)...")
    app.abrir_modal_finalizacao()
    app.fechar_modal_e_finalizar(salvar=False)
    assert app.modal_confirmacao_ativo is False
    assert app.salvar_ao_finalizar is False
    assert app.deve_encerrar is True

    # 8. Testar fechar_modal_e_finalizar com salvar=True
    print("  [+] Testando fechar_modal_e_finalizar(salvar=True)...")
    app.fechar_modal_e_finalizar(salvar=True)
    assert app.salvar_ao_finalizar is True
    assert app.deve_encerrar is True

    # Limpeza
    shutil.rmtree(pasta_tmp, ignore_errors=True)
    print("\n[✓ SUCESSO] Todos os comportamentos do modal e alterações pendentes validados com sucesso!")


if __name__ == "__main__":
    test_rastreamento_alteracoes_e_modal()
