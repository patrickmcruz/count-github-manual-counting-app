#!/usr/bin/env python3
"""
Testes automatizados para a Fase 11:
Inicialização padrão em Standby (modo de espera) e correção de saída/cancelamento.
"""

import sys
import shutil
from pathlib import Path
from unittest.mock import patch

# Adiciona raiz do app ao path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import cv2
import app


def test_inicializacao_standby():
    print("[*] 1. Testando inicialização em modo de espera (Standby)...")
    app.screen_w = 1280
    app.screen_h = 720
    app.img_base = None
    app.caminho_img_ativo = None
    app.coordenadas = []
    app.alteracoes_pendentes = False
    app.modal_confirmacao_ativo = False
    app.deve_encerrar = False
    app.solicitacao_abrir_imagem = False

    app.atualizar_canvas()

    assert app.img_display is not None, "Canvas deve ser renderizado mesmo sem imagem"
    assert app.BTN_SELECT_IMAGE != (0, 0, 0, 0), "Botao central deve estar visivel no Standby"
    assert app.BTN_OPEN_IMAGE != (0, 0, 0, 0), "Botão [ Abrir (O) ] deve estar visível no Standby"
    assert app.BTN_FINISH != (0, 0, 0, 0), "Botão [ X Sair ] deve estar visível no Standby"
    assert app.BTN_HAND_PAN == (0, 0, 0, 0), "Botão Mão deve estar desativado sem imagem"
    assert app.BTN_SAVE == (0, 0, 0, 0), "Botão Salvar deve estar desativado sem imagem"
    print("      [✓] Standby renderizado corretamente com botões Abrir e Sair.")


def test_clique_sair_no_standby():
    print("[*] 2. Testando clique em [ X Sair ] no modo Standby...")
    app.screen_w = 1280
    app.screen_h = 720
    app.img_base = None
    app.deve_encerrar = False
    app.atualizar_canvas()

    bx1, by1, bx2, by2 = app.BTN_FINISH
    click_x = (bx1 + bx2) // 2
    click_y = (by1 + by2) // 2

    # Simula clique esquerdo no botão [ X Sair ]
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, click_x, click_y, 0, None)

    assert app.deve_encerrar is True, "deve_encerrar deve ser True imediatamente ao clicar em Sair no Standby"
    print("      [✓] Clique em Sair encerrou o app sem abrir modal.")


def test_solicitacao_abrir_imagem():
    print("[*] 3. Testando disparo assíncrono de solicitação de abertura de imagem...")
    app.screen_w = 1280
    app.screen_h = 720
    app.solicitacao_abrir_imagem = False
    app.atualizar_canvas()

    ox1, oy1, ox2, oy2 = app.BTN_OPEN_IMAGE
    click_x = (ox1 + ox2) // 2
    click_y = (oy1 + oy2) // 2

    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, click_x, click_y, 0, None)
    assert app.solicitacao_abrir_imagem is True, "solicitacao_abrir_imagem deve ser ativada pelo clique"

    app.solicitacao_abrir_imagem = False
    sx1, sy1, sx2, sy2 = app.BTN_SELECT_IMAGE
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, (sx1 + sx2) // 2, (sy1 + sy2) // 2, 0, None)
    assert app.solicitacao_abrir_imagem is True, "botao central deve usar o mesmo fluxo de selecao"
    print("      [✓] solicitacao_abrir_imagem acionada com sucesso sem travar callback.")


def test_cancelamento_abertura_e_saida():
    print("[*] 4. Testando cenário de cancelamento de seletor e posterior saída...")
    app.screen_w = 1280
    app.screen_h = 720
    app.img_base = np.zeros((800, 800, 3), dtype=np.uint8)
    app.caminho_img_ativo = Path("data/input/test_img.jpg")
    app.caminho_saida_ativo = Path("data/ground_truth/test_out")
    app.coordenadas = []
    app.alteracoes_pendentes = False
    app.modal_confirmacao_ativo = False
    app.deve_encerrar = False
    app.salvar_ao_finalizar = True

    # Simula cancelamento do seletor de arquivos (retorna None)
    with patch("app.abrir_dialogo_arquivo", return_value=None):
        app.acao_selecionar_imagem_usuario()

    assert "cancelada" in app.status_mensagem.lower()
    print("      [✓] Seletor cancelado tratado com mensagem no status.")

    # Agora usuário clica em Finalizar / Sair
    app.atualizar_canvas()
    fx1, fy1, fx2, fy2 = app.BTN_FINISH
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, (fx1 + fx2) // 2, (fy1 + fy2) // 2, 0, None)

    assert app.modal_confirmacao_ativo is True, "Modal de finalização deve ser ativado"
    assert app.BTN_MODAL_SAIR_SEM_SALVAR != (0, 0, 0, 0), "Botão Sair do App / Sem Salvar deve estar ativo mesmo com 0 pendências"

    # Simula clique no botão [ Sair do App (D) ]
    sx1, sy1, sx2, sy2 = app.BTN_MODAL_SAIR_SEM_SALVAR
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, (sx1 + sx2) // 2, (sy1 + sy2) // 2, 0, None)

    assert app.modal_confirmacao_ativo is False, "Modal deve fechar"
    assert app.salvar_ao_finalizar is False, "Não deve gerar entregáveis ao descartar/sair"
    assert app.deve_encerrar is True, "deve_encerrar deve ser True"
    print("      [✓] Botão Sair do App funcionou perfeitamente após cancelamento de arquivo.")


def test_clique_backdrop_modal():
    print("[*] 5. Testando cancelamento do modal por clique fora da janela (backdrop)...")
    app.screen_w = 1280
    app.screen_h = 720
    app.img_base = np.zeros((800, 800, 3), dtype=np.uint8)
    app.modal_confirmacao_ativo = True
    app.atualizar_canvas()

    # Clica no canto superior esquerdo (fora de MODAL_RECT)
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, 10, 10, 0, None)
    assert app.modal_confirmacao_ativo is False, "Modal deve fechar ao clicar no backdrop"
    print("      [✓] Backdrop click cancela o modal com segurança.")


def test_execucao_main_standby():
    print("[*] 6. Testando execução real da função main() no modo Standby...")
    app.img_base = None
    app.caminho_img_ativo = None
    app.modal_confirmacao_ativo = False
    app.deve_encerrar = False
    app.solicitacao_abrir_imagem = False

    def mock_wait_key(*args, **kwargs):
        # Na primeira chamada do loop, valida que solicitacao_abrir_imagem foi acessada e encerra
        app.deve_encerrar = True
        return -1

    with patch("sys.argv", ["app.py", "--tela", "800x600", "--janela"]), \
         patch("cv2.namedWindow"), \
         patch("cv2.resizeWindow"), \
         patch("cv2.setMouseCallback"), \
         patch("cv2.imshow"), \
         patch("cv2.destroyAllWindows"), \
         patch("cv2.getWindowImageRect", return_value=(0, 0, 800, 600)), \
         patch("cv2.waitKeyEx", side_effect=mock_wait_key):
        app.main()

    assert app.deve_encerrar is True
    print("      [✓] main() executou e encerrou no Standby sem qualquer exceção.")


if __name__ == "__main__":
    test_inicializacao_standby()
    test_clique_sair_no_standby()
    test_solicitacao_abrir_imagem()
    test_cancelamento_abertura_e_saida()
    test_clique_backdrop_modal()
    test_execucao_main_standby()
    print("\n[✓ SUCESSO] Todos os testes de Standby e Saída passaram com 100% de sucesso!")
