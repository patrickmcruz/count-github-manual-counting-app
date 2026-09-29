#!/usr/bin/env python3
"""
Testes automatizados para a Fase 09:
Validação do Modo Mão / Pan interativo no cabeçalho e prevenção de contagem acidental.
"""

import sys
import shutil
from pathlib import Path

# Adiciona raiz do app ao path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import cv2
import app

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def test_modo_mao_e_prevencao_contagem():
    print("[*] Iniciando teste do Modo Mão / Pan e prevenção de contagem acidental...")

    # Configuração de estado sintético para simulação
    app.screen_w = 1280
    app.screen_h = 720
    app.center_x = 500.0
    app.center_y = 500.0
    app.zoom_level = 2.0
    app.img_base = np.zeros((1000, 1000, 3), dtype=np.uint8)
    app.coordenadas = []
    app.alteracoes_pendentes = False
    app.modal_confirmacao_ativo = False
    app.modo_mao_ativo = False
    app.is_dragging_pan = False

    # Renderiza canvas inicial para calcular dimensões e botões
    app.atualizar_canvas()
    assert app.BTN_HAND_PAN != (0, 0, 0, 0), "BTN_HAND_PAN deve estar definido no HUD"
    btn_x = (app.BTN_HAND_PAN[0] + app.BTN_HAND_PAN[2]) // 2
    btn_y = (app.BTN_HAND_PAN[1] + app.BTN_HAND_PAN[3]) // 2

    # 1. Teste: Alternância de modo
    print("  [+] Testando alternar_modo_mao()...")
    assert app.modo_mao_ativo is False, "Deveria iniciar no Modo Marcador (False)"
    app.alternar_modo_mao()
    assert app.modo_mao_ativo is True, "Modo Mão deveria estar True após alternar"
    app.alternar_modo_mao()
    assert app.modo_mao_ativo is False, "Modo Mão deveria estar False após alternar novamente"

    # 2. Teste: Clique no botão BTN_HAND_PAN pelo mouse
    print("  [+] Testando clique do mouse no botão BTN_HAND_PAN do HUD...")
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, btn_x, btn_y, 0, None)
    assert app.modo_mao_ativo is True, "Modo Mão deveria ter sido ativado pelo clique no botão do HUD"

    # Ponto no meio do canvas da imagem
    click_img_x = app.screen_w // 2
    click_img_y = app.screen_h // 2
    assert click_img_y > app.HUD_HEIGHT, "Ponto deve estar abaixo do HUD"

    # 3. Teste CRÍTICO: No Modo Mão, clique esquerdo NÃO pode adicionar ponto e DEVE iniciar pan
    print("  [+] Testando clique na imagem com Modo Mão ATIVADO...")
    total_pontos_antes = len(app.coordenadas)
    centro_x_antes = app.center_x
    centro_y_antes = app.center_y

    # Pressionar botão esquerdo na imagem
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, click_img_x, click_img_y, 0, None)
    assert len(app.coordenadas) == total_pontos_antes, "ERRO: Ponto NÃO pode ser adicionado quando Modo Mão estiver ativo!"
    assert app.is_dragging_pan is True, "Arrasto de Pan deveria ter sido iniciado no clique esquerdo"

    # Arrastar mouse para a esquerda e para cima
    app.callback_mouse(cv2.EVENT_MOUSEMOVE, click_img_x - 50, click_img_y - 50, 0, None)
    assert app.center_x != centro_x_antes or app.center_y != centro_y_antes, "Pan deveria ter movido a visualização"

    # Soltar botão esquerdo
    app.callback_mouse(cv2.EVENT_LBUTTONUP, click_img_x - 50, click_img_y - 50, 0, None)
    assert app.is_dragging_pan is False, "Arrasto de Pan deveria ter terminado após soltar o botão esquerdo"
    assert len(app.coordenadas) == total_pontos_antes, "Nenhum ponto deve ter sido registrado em todo o ciclo de pan!"
    print("      [✓] Nenhum ponto acidental foi registrado durante o pan!")

    # 4. Teste: Desativar Modo Mão e verificar que o clique volta a marcar pontos
    print("  [+] Desativando Modo Mão e testando marcação de pontos...")
    app.alternar_modo_mao()
    assert app.modo_mao_ativo is False

    # Clique esquerdo na imagem agora deve marcar um ponto
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, click_img_x, click_img_y, 0, None)
    assert len(app.coordenadas) == total_pontos_antes + 1, "Ponto deveria ser registrado com Modo Mão desativado"
    print(f"      [✓] Ponto #{app.coordenadas[-1]['id']} registrado com sucesso no Modo Marcador!")

    print("\n[✓ SUCESSO] Comportamento do Modo Mão e prevenção de contagem acidental 100% validados!")


if __name__ == "__main__":
    test_modo_mao_e_prevencao_contagem()
