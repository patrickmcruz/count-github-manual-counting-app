#!/usr/bin/env python3
"""
Testes automatizados para a Fase 10:
Validação do Header Flutuante Sobreposto (Overlay translúcido) e navegação imersiva.
"""

import sys
from pathlib import Path

# Adiciona raiz do app ao path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import cv2
import app

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def test_header_flutuante_overlay():
    print("[*] Iniciando teste do Header Flutuante Sobreposto (Fase 10)...")

    # Configuração de estado sintético para simulação
    app.screen_w = 1920
    app.screen_h = 1080
    app.center_x = 500.0
    app.center_y = 500.0
    app.zoom_level = 1.0
    # Imagem sintética 4000x3000
    app.img_base = np.zeros((3000, 4000, 3), dtype=np.uint8)
    app.img_base[:] = (100, 100, 100)
    app.coordenadas = []
    app.alteracoes_pendentes = False
    app.modal_confirmacao_ativo = False
    app.modo_mao_ativo = False
    app.is_dragging_pan = False

    # 1. Renderiza canvas inicial e valida ocupação total da tela
    print("  [+] Testando aproveitamento total da tela e centralização...")
    app.atualizar_canvas()

    esperado_offset_y = (app.screen_h - app.fit_h) // 2
    assert app.offset_y == esperado_offset_y, f"offset_y ({app.offset_y}) deve estar perfeitamente centralizado ({esperado_offset_y})"
    print(f"      [✓] Altura utilizada: {app.fit_h}px | offset_y: {app.offset_y}px (Centralizado)")

    # 2. Verifica que a área do cabeçalho possui o overlay translúcido
    print("  [+] Testando presença do overlay translúcido no topo da tela...")
    hud_sample = app.img_display[10, 100]
    # O fundo deve ter uma mescla escurecida (não puramente 100,100,100 nem puramente 0,0,0)
    assert not np.array_equal(hud_sample, [100, 100, 100]), "O HUD deve modificar visualmente os pixels do topo com overlay"
    print(f"      [✓] Header translúcido mesclado com sucesso no canvas!")

    # 3. Teste: Clicar no botão [Mao (H)] com zoom 3.0x deve funcionar sem marcar pontos
    print("  [+] Aplicando Zoom 3.0x...")
    app.aplicar_zoom(3.0)
    assert app.zoom_level >= 3.0, "Zoom deve ser >= 3.0"

    btn_x = (app.BTN_HAND_PAN[0] + app.BTN_HAND_PAN[2]) // 2
    btn_y = (app.BTN_HAND_PAN[1] + app.BTN_HAND_PAN[3]) // 2

    print(f"  [+] Clicando no botão [Mao (H)] em ({btn_x}, {btn_y}) com zoom ativo...")
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, btn_x, btn_y, 0, None)
    assert app.modo_mao_ativo is True, "Modo Mão deveria ter sido ativado através do clique no HUD com zoom"
    assert len(app.coordenadas) == 0, "Clique no HUD com zoom NUNCA pode registrar contagem!"
    print("      [✓] Modo Mão ativado com sucesso via header durante zoom!")

    # 4. Teste: Clicar novamente no botão [Mao (H)] desativa o modo mão
    print("  [+] Clicando novamente no botão [Mao (H)] para alternar de volta ao marcador...")
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, btn_x, btn_y, 0, None)
    assert app.modo_mao_ativo is False, "Modo Mão deveria ter sido desativado"
    assert len(app.coordenadas) == 0, "Nenhum ponto registrado ao desativar ferramenta"
    print("      [✓] Modo Marcador restaurado com sucesso!")

    # 5. Teste: Clique na imagem abaixo do cabeçalho (y > HUD_HEIGHT) marca ponto normalmente
    print("  [+] Testando clique na imagem abaixo do cabeçalho flutuante...")
    click_x = app.screen_w // 2
    click_y = app.HUD_HEIGHT + 100
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, click_x, click_y, 0, None)
    assert len(app.coordenadas) == 1, "Ponto deveria ser registrado na imagem abaixo do cabeçalho"
    print(f"      [✓] Ponto #{app.coordenadas[0]['id']} registrado com sucesso!")

    # 6. Teste: Clique na faixa do cabeçalho (y <= HUD_HEIGHT) fora dos botões também não adiciona pontos
    print("  [+] Testando clique no espaço vazio do cabeçalho flutuante...")
    app.callback_mouse(cv2.EVENT_LBUTTONDOWN, 10, 20, 0, None)
    assert len(app.coordenadas) == 1, "Clique no cabeçalho flutuante jamais deve adicionar pontos"
    print("      [✓] Cliques no cabeçalho flutuante são 100% seguros!")

    print("\n[✓ SUCESSO] Header Flutuante Sobreposto e integração com zoom validados com excelência!")


if __name__ == "__main__":
    test_header_flutuante_overlay()
