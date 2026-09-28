#!/usr/bin/env python3
"""
Anotador Manual de Pontos (Ground Truth) para Contagem de Pessoas
===============================================================
Ferramenta interativa de anotação de multidões com Zoom e Panorâmica (Pan)
em tempo real para imagens de altíssima resolução (8000x6000 px ou qualquer dimensão).

Projetado para funcionar com alta performance em Windows, Linux e macOS.

Controles de Navegação:
- Roda do Mouse (Scroll): Zoom In / Zoom Out centrado no cursor do mouse.
- Botão do Meio (Scroll Click) e Arrastar: Mover pela cena (Panorâmica / Pan).
- Segurar Tecla ESPAÇO + Botão Esquerdo: Mover pela cena (Pan estilo Photoshop/Figma).
- Teclas W, A, S, D ou Setas: Mover a câmera pelo teclado.
- Tecla R ou Botão [ Fit ]: Resetar para a visão geral da imagem inteira.
- Teclas I / O ou Botões [ + ] e [ - ]: Zoom In / Zoom Out.
- Mini-Mapa (Picture-in-Picture): No canto inferior direito indicando a região visível.

Controles de Anotação:
- Botão Esquerdo: Marcar ponto (cabeça) na resolução nativa original.
- Botão [ <- Desfazer ] (ou Ctrl+Z / U / Backspace / Botão Direito): Desfazer último ponto.
- Botão [ Salvar ] (ou Ctrl+S / S): Salvar progresso atual (checkpoint imediato).
- Botão [ Finalizar ] (ou F / ESC): Finalizar a contagem e gerar entregáveis oficiais.
- Teclas [ + ] e [ - ]: Ajustar tamanho visual do marcador na tela.
- Tecla F11: Alternar Tela Cheia / Janela.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

# Resolução de diretórios do aplicativo
APP_ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = APP_ROOT / "data" / "input"
DEFAULT_OUTPUT_DIR = APP_ROOT / "data" / "ground_truth"

# Estado da aplicação
coordenadas = []
img_base = None             # Imagem original em memória
img_thumb = None            # Miniatura para o mini-mapa PiP
img_display = None          # Frame renderizado para cv2.imshow
raio_marcador_display = 2   # Raio na tela do monitor
is_fullscreen = True

# Estado de Zoom e Navegação (Pan)
zoom_level = 1.0            # Escala de zoom (1.0 = Fit tela, até 12.0x)
center_x = 0.0              # Posição central X na imagem original
center_y = 0.0              # Posição central Y na imagem original
is_dragging_pan = False
pan_start_screen = (0, 0)
pan_start_center = (0.0, 0.0)
space_is_pressed = False

# Dimensões da tela e viewport
screen_w = 1920
screen_h = 1080
HUD_HEIGHT = 50

# Coordenadas do viewport atual na imagem original
roi_x1, roi_y1, roi_x2, roi_y2 = 0.0, 0.0, 1920.0, 1080.0
fit_w, fit_h = 1371, 1028
offset_x, offset_y = 274, 50
scale_fit = 0.1713

deve_encerrar = False
status_mensagem = "Rolar mouse: Zoom | Meio/Espaco: Arrastar | R: Reset Fit | [+/-]: Marcador"
status_cor = (203, 213, 225)

# Diretório e imagem ativos
caminho_img_ativo = None
caminho_saida_ativo = None

WINDOW_NAME = "Anotador de Multidoes (Ground Truth)"

# Estado de Salvamento e Confirmação de Saída
alteracoes_pendentes = False
modal_confirmacao_ativo = False
salvar_ao_finalizar = True
solicitacao_abrir_imagem = False

# Modo de Ferramenta: Apontador/Marcador (False) ou Mão/Pan (True)
modo_mao_ativo = False

# Botões interativos no HUD
BTN_OPEN_IMAGE = (0, 0, 0, 0)
BTN_HAND_PAN = (0, 0, 0, 0)
BTN_ZOOM_IN = (0, 0, 0, 0)
BTN_ZOOM_OUT = (0, 0, 0, 0)
BTN_RESET_ZOOM = (0, 0, 0, 0)
BTN_UNDO = (0, 0, 0, 0)
BTN_SAVE = (0, 0, 0, 0)
BTN_FINISH = (0, 0, 0, 0)

# Botões do Modal de Confirmação de Saída
BTN_MODAL_CONFIRMAR_SALVAR = (0, 0, 0, 0)
BTN_MODAL_SAIR_SEM_SALVAR = (0, 0, 0, 0)
BTN_MODAL_CANCELAR = (0, 0, 0, 0)
MODAL_RECT = (0, 0, 0, 0)



def obter_resolucao_tela(default_w: int = 1920, default_h: int = 1080):
    """Detecta automaticamente a resolução do monitor no Windows, Linux e macOS."""
    # 1. Windows: Detecção nativa de tela com suporte a DPI
    if sys.platform.startswith("win"):
        try:
            import ctypes
            user32 = ctypes.windll.user32
            try:
                user32.SetProcessDPIAware()
            except Exception:
                pass
            w = user32.GetSystemMetrics(0)
            h = user32.GetSystemMetrics(1)
            if w >= 800 and h >= 600:
                return w, h
        except Exception:
            pass

    # 2. Universal: Tkinter (disponível por padrão no Python desktop)
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        if w >= 800 and h >= 600:
            return w, h
    except Exception:
        pass

    # 3. Linux: Inspeção direta no kernel DRM
    try:
        for p in sorted(Path("/sys/class/drm").glob("card*-*/modes")):
            lines = p.read_text().splitlines()
            if lines:
                parts = lines[0].strip().split("x")
                if len(parts) == 2:
                    w, h = int(parts[0]), int(parts[1])
                    if w >= 800 and h >= 600:
                        return w, h
    except Exception:
        pass

    return default_w, default_h


def abrir_dialogo_arquivo(pasta_inicial: Path = None) -> Path:
    """Abre caixa de diálogo nativa de seleção de arquivo (Windows, Linux, macOS)."""
    # 1. Tentativa via Tkinter (padrão em Windows)
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        diretorio = str(pasta_inicial.resolve()) if (pasta_inicial and pasta_inicial.exists()) else str(APP_ROOT)
        caminho = filedialog.askopenfilename(
            title="Selecione a Imagem para Contagem de Pessoas",
            initialdir=diretorio,
            filetypes=[
                ("Imagens Aéreas", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.JPG *.JPEG *.PNG"),
                ("Todos os arquivos", "*.*")
            ]
        )
        root.update()
        root.destroy()
        if caminho:
            p = Path(caminho)
            if p.exists() and p.is_file():
                return p
    except Exception:
        pass

    # 2. Tentativa via zenity no Linux (padrão em GNOME/Ubuntu)
    if sys.platform.startswith("linux"):
        import shutil
        import subprocess
        if shutil.which("zenity"):
            try:
                filtro = "--file-filter=Imagens (*.jpg, *.png) | *.jpg *.jpeg *.png *.bmp *.tif *.tiff *.JPG *.JPEG *.PNG"
                cmd = ["zenity", "--file-selection", "--title=Selecione a Imagem para Contar", filtro]
                if pasta_inicial and pasta_inicial.exists():
                    cmd.append(f"--filename={pasta_inicial.resolve()}/")
                res = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if res.returncode == 0 and res.stdout.strip():
                    p = Path(res.stdout.strip())
                    if p.exists() and p.is_file():
                        return p
            except Exception:
                pass

        # 3. Tentativa via kdialog no Linux (KDE)
        if shutil.which("kdialog"):
            try:
                cmd = ["kdialog", "--getopenfilename", str(pasta_inicial or "."), "*.jpg *.jpeg *.png *.JPG *.JPEG *.PNG"]
                res = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if res.returncode == 0 and res.stdout.strip():
                    p = Path(res.stdout.strip())
                    if p.exists() and p.is_file():
                        return p
            except Exception:
                pass

    # Garante liberação de eventos e restabelecimento de foco no OpenCV
    try:
        cv2.waitKey(1)
    except Exception:
        pass

    return None


def selecionar_imagem(caminho_solicitado: Path = None, pasta_input: Path = None) -> Path:
    """Identifica a imagem a ser anotada via argumento, pasta data/input/, seletor gráfico ou menu de terminal."""
    if caminho_solicitado and caminho_solicitado.exists() and caminho_solicitado.is_file():
        return caminho_solicitado

    extensoes = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

    # Se uma imagem foi passada por nome simples, procura em data/input/
    if caminho_solicitado and pasta_input and pasta_input.exists():
        tentativa = pasta_input / caminho_solicitado.name
        if tentativa.exists() and tentativa.is_file():
            return tentativa

    # Procura imagens existentes em data/input/
    imagens_encontradas = []
    if pasta_input and pasta_input.exists():
        imagens_encontradas = sorted([
            p for p in pasta_input.iterdir()
            if p.is_file() and p.suffix.lower() in extensoes and not p.name.startswith(".")
        ])
        if len(imagens_encontradas) == 1:
            print(f"[*] Imagem única encontrada automaticamente em data/input/: {imagens_encontradas[0].name}")
            return imagens_encontradas[0]

    # 1. Tentativa via Seletor Visual Nativo do Sistema
    escolhida_dialogo = abrir_dialogo_arquivo(pasta_input)
    if escolhida_dialogo:
        return escolhida_dialogo

    # 2. Fallback: Menu no Terminal com as imagens encontradas em data/input/
    if imagens_encontradas:
        print("\n" + "=" * 64)
        print(f"   IMAGENS DISPONÍVEIS NA PASTA {pasta_input.name}/")
        print("=" * 64)
        for idx, img_path in enumerate(imagens_encontradas, 1):
            print(f"  [{idx}] {img_path.name}")
        print("=" * 64)

        if sys.stdin.isatty():
            try:
                msg_prompt = f"\nEscolha o número da imagem [1-{len(imagens_encontradas)}] (Pressione Enter para [1]): "
                escolha = input(msg_prompt).strip()
                if not escolha:
                    print(f"[*] Selecionada opção padrão: {imagens_encontradas[0].name}")
                    return imagens_encontradas[0]
                num = int(escolha)
                if 1 <= num <= len(imagens_encontradas):
                    selecionada = imagens_encontradas[num - 1]
                    print(f"[✓] Imagem selecionada: {selecionada.name}")
                    return selecionada
                else:
                    print(f"[!] Opção fora da faixa. Selecionando {imagens_encontradas[0].name} por padrão.")
                    return imagens_encontradas[0]
            except (ValueError, EOFError, KeyboardInterrupt):
                print(f"[*] Selecionando {imagens_encontradas[0].name} por padrão.")
                return imagens_encontradas[0]
        else:
            print(f"[*] Modo não-interativo: selecionando {imagens_encontradas[0].name}")
            return imagens_encontradas[0]

    # 3. Fallback: Entrada manual de caminho no terminal
    if sys.stdin.isatty():
        try:
            print("\nNenhuma imagem encontrada na pasta data/input/ e seletor gráfico indisponível.")
            caminho_manual = input("Digite ou cole o caminho completo da imagem (.JPG): ").strip().strip('"').strip("'")
            if caminho_manual:
                p = Path(caminho_manual)
                if p.exists() and p.is_file():
                    return p
        except (EOFError, KeyboardInterrupt):
            pass

    return None


def carregar_imagem_no_app(caminho_nova_img: Path, pasta_saida_base: Path = None, salvar_atual: bool = True) -> bool:
    """Carrega uma nova imagem no aplicativo, salvando o progresso da anterior e ajustando a UI."""
    global img_base, img_thumb, caminho_img_ativo, caminho_saida_ativo, coordenadas
    global center_x, center_y, zoom_level, status_mensagem, status_cor, alteracoes_pendentes

    if caminho_nova_img is None or not caminho_nova_img.exists():
        return False

    if salvar_atual and caminho_img_ativo is not None and len(coordenadas) > 0:
        print("[*] Gravando checkpoint da imagem anterior antes da troca...")
        salvar_checkpoint(silencioso=False)

    print(f"[*] Carregando imagem: {caminho_nova_img.name}")
    nova_img = cv2.imread(str(caminho_nova_img))
    if nova_img is None:
        print(f"[ERRO] Falha ao decodificar a imagem: {caminho_nova_img}")
        status_mensagem = f"Erro ao abrir: {caminho_nova_img.name}"
        status_cor = (248, 113, 113)
        atualizar_canvas()
        return False

    img_base = nova_img
    caminho_img_ativo = caminho_nova_img

    h_orig, w_orig = img_base.shape[:2]
    center_x = w_orig / 2.0
    center_y = h_orig / 2.0
    zoom_level = 1.0

    # Miniatura PiP
    thumb_w = 180
    thumb_h = int(round(180 * (h_orig / w_orig)))
    img_thumb = cv2.resize(img_base, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)

    # Subdiretório de saída
    stem = caminho_nova_img.stem
    raiz_saida = pasta_saida_base if pasta_saida_base is not None else DEFAULT_OUTPUT_DIR
    if raiz_saida.name == "ground_truth":
        caminho_saida_ativo = raiz_saida / stem
    else:
        caminho_saida_ativo = raiz_saida
    caminho_saida_ativo.mkdir(parents=True, exist_ok=True)

    # Continuação automática: busca anotações existentes para esta imagem
    coordenadas = []
    p_chk_stem = caminho_saida_ativo / f"checkpoint_{stem}.json"
    p_chk_anot = caminho_saida_ativo / "checkpoint_anotacao.json"
    p_csv_stem = caminho_saida_ativo / f"pontos_ground_truth_{stem}.csv"

    arquivo_alvo = None
    for cand in (p_chk_stem, p_chk_anot, p_csv_stem):
        if cand.exists():
            arquivo_alvo = cand
            break

    n_rec = 0
    if arquivo_alvo:
        n_rec = carregar_anotacoes(arquivo_alvo, img_base.shape)

    if n_rec > 0:
        status_mensagem = f"✓ Carregado: {caminho_nova_img.name} ({n_rec} pts recuperados)"
        status_cor = (74, 222, 128)
        print(f"[✓ CONTINUAÇÃO AUTOMÁTICA] Recuperadas {n_rec} anotações de {arquivo_alvo.name}!")
    else:
        status_mensagem = f"Imagem carregada: {caminho_nova_img.name} (0 pts)"
        status_cor = (147, 197, 253)

    alteracoes_pendentes = False
    atualizar_canvas()
    return True


def acao_selecionar_imagem_usuario():
    """Abre o seletor nativo para o usuário escolher qualquer imagem no computador."""
    global status_mensagem, status_cor
    status_mensagem = "Aguardando selecao de imagem no computador..."
    status_cor = (250, 204, 21)
    atualizar_canvas()
    cv2.waitKey(1)

    pasta_sugestao = DEFAULT_INPUT_DIR if DEFAULT_INPUT_DIR.exists() else APP_ROOT
    escolhida = abrir_dialogo_arquivo(pasta_inicial=pasta_sugestao)
    if escolhida:
        carregar_imagem_no_app(escolhida)
    else:
        status_mensagem = "Selecao cancelada"
        status_cor = (203, 213, 225)
        atualizar_canvas()




def calcular_roi():
    """Calcula a janela visível (ROI) na imagem original baseada no zoom e centro."""
    global roi_x1, roi_y1, roi_x2, roi_y2, center_x, center_y
    h_orig, w_orig = img_base.shape[:2]

    roi_w = w_orig / zoom_level
    roi_h = h_orig / zoom_level

    x1 = center_x - roi_w / 2.0
    y1 = center_y - roi_h / 2.0
    x2 = x1 + roi_w
    y2 = y1 + roi_h

    # Clamping dentro das bordas da imagem original
    if x1 < 0:
        x2 -= x1
        x1 = 0.0
    if x2 > w_orig:
        x1 -= (x2 - w_orig)
        x2 = float(w_orig)
    if y1 < 0:
        y2 -= y1
        y1 = 0.0
    if y2 > h_orig:
        y1 -= (y2 - h_orig)
        y2 = float(h_orig)

    roi_x1 = max(0.0, x1)
    roi_y1 = max(0.0, y1)
    roi_x2 = min(float(w_orig), x2)
    roi_y2 = min(float(h_orig), y2)

    center_x = (roi_x1 + roi_x2) / 2.0
    center_y = (roi_y1 + roi_y2) / 2.0


def aplicar_zoom(fator: float, cursor_screen_x: int = None, cursor_screen_y: int = None):
    """Aplica zoom in ou zoom out centrado no cursor do mouse ou no centro atual."""
    global zoom_level, center_x, center_y, status_mensagem, status_cor

    novo_zoom = np.clip(zoom_level * fator, 1.0, 12.0)
    if abs(novo_zoom - zoom_level) < 0.01:
        return

    if cursor_screen_x is not None and cursor_screen_y is not None:
        if offset_x <= cursor_screen_x < offset_x + fit_w and offset_y <= cursor_screen_y < offset_y + fit_h:
            norm_x = (cursor_screen_x - offset_x) / fit_w
            norm_y = (cursor_screen_y - offset_y) / fit_h
            orig_mouse_x = roi_x1 + norm_x * (roi_x2 - roi_x1)
            orig_mouse_y = roi_y1 + norm_y * (roi_y2 - roi_y1)

            center_x = orig_mouse_x - (norm_x - 0.5) * (img_base.shape[1] / novo_zoom)
            center_y = orig_mouse_y - (norm_y - 0.5) * (img_base.shape[0] / novo_zoom)

    zoom_level = novo_zoom
    status_mensagem = f"Zoom: {zoom_level:.1f}x | Rolar mouse para aproximar/afastar"
    status_cor = (147, 197, 253)
    atualizar_canvas()


def reset_zoom():
    """Reseta a visualização para o enquadramento completo (Fit)."""
    global zoom_level, center_x, center_y, status_mensagem, status_cor
    h_orig, w_orig = img_base.shape[:2]
    zoom_level = 1.0
    center_x = w_orig / 2.0
    center_y = h_orig / 2.0
    status_mensagem = "Visão geral da imagem (Fit completo)"
    status_cor = (203, 213, 225)
    atualizar_canvas()


def mover_pan(dx_screen: int, dy_screen: int):
    """Move a câmera pela cena com base no deslocamento na tela."""
    global center_x, center_y
    if fit_w <= 0 or fit_h <= 0:
        return
    delta_orig_x = (dx_screen / fit_w) * (roi_x2 - roi_x1)
    delta_orig_y = (dy_screen / fit_h) * (roi_y2 - roi_y1)

    center_x -= delta_orig_x
    center_y -= delta_orig_y
    atualizar_canvas()


def alternar_modo_mao():
    """Alterna entre o Modo Marcador (adicionar pontos) e o Modo Mão (navegação/pan livre sem marcar)."""
    global modo_mao_ativo, status_mensagem, status_cor
    modo_mao_ativo = not modo_mao_ativo
    if modo_mao_ativo:
        status_mensagem = "Modo Mao ATIVADO: clique e arraste para mover a imagem (pontos bloqueados)"
        status_cor = (0, 180, 255)
        print("[*] Ferramenta Mão ativada (clique esquerdo move a câmera sem marcar).")
    else:
        status_mensagem = "Modo Marcador ATIVADO: clique na imagem para marcar pessoas"
        status_cor = (74, 222, 128)
        print("[*] Ferramenta Marcador ativada (clique esquerdo adiciona pontos).")
    atualizar_canvas()


def salvar_checkpoint(silencioso: bool = False):
    """Salva o progresso atual em disco (checkpoint) sem fechar a aplicação."""
    global status_mensagem, status_cor, alteracoes_pendentes
    if caminho_saida_ativo is None or caminho_img_ativo is None:
        return

    caminho_saida_ativo.mkdir(parents=True, exist_ok=True)
    stem = caminho_img_ativo.stem
    p_csv_stem = caminho_saida_ativo / f"pontos_ground_truth_{stem}.csv"
    p_json_stem = caminho_saida_ativo / f"checkpoint_{stem}.json"
    p_json_anotacao = caminho_saida_ativo / "checkpoint_anotacao.json"

    # 1. Salva CSV com coordenadas parciais
    df = pd.DataFrame(coordenadas)
    df.to_csv(p_csv_stem, index=False)

    # 2. Salva JSON de Checkpoint
    checkpoint_data = {
        "tipo": "checkpoint_progresso",
        "data_checkpoint": time.strftime("%Y-%m-%d %H:%M:%S"),
        "imagem_origem": str(caminho_img_ativo),
        "arquivo_nome": caminho_img_ativo.name,
        "resolucao_original": {
            "largura": int(img_base.shape[1]),
            "altura": int(img_base.shape[0]),
        },
        "total_pessoas_anotadas": len(coordenadas),
        "pontos": coordenadas,
    }
    for dest in (p_json_stem, p_json_anotacao):
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

    alteracoes_pendentes = False
    hora_str = time.strftime("%H:%M:%S")
    status_mensagem = f"✓ Salvo as {hora_str} ({len(coordenadas)} pts)"
    status_cor = (74, 222, 128)

    if not silencioso:
        print(f"[✓ CHECKPOINT] {len(coordenadas)} anotações salvas em: {p_csv_stem.name} ({hora_str})")
    atualizar_canvas()


def atualizar_canvas():
    """Renderiza a região visível em alta resolução, projeta os pontos e o HUD."""
    global img_display, BTN_OPEN_IMAGE, BTN_HAND_PAN, BTN_ZOOM_IN, BTN_ZOOM_OUT, BTN_RESET_ZOOM, BTN_UNDO, BTN_SAVE, BTN_FINISH
    global fit_w, fit_h, offset_x, offset_y, scale_fit

    w = screen_w
    avail_w = screen_w
    avail_h = screen_h

    # Modo Standby: caso o app inicie sem imagem carregada
    if img_base is None:
        img_display = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
        img_display[:] = (18, 22, 30)

        # Barra de HUD superior
        cv2.rectangle(img_display, (0, 0), (w, HUD_HEIGHT), (15, 23, 42), -1)
        cv2.line(img_display, (0, HUD_HEIGHT), (w, HUD_HEIGHT), (56, 189, 248), 2)

        cv2.putText(img_display, "Anotador de Multidoes", (16, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (148, 163, 184), 2, cv2.LINE_AA)
        cv2.putText(img_display, status_mensagem, (320, 31), cv2.FONT_HERSHEY_SIMPLEX, 0.48, status_cor, 1, cv2.LINE_AA)

        # Botão: Abrir Imagem (O)
        op_x1, op_y1, op_x2, op_y2 = w - 970, 8, w - 860, 42
        BTN_OPEN_IMAGE = (op_x1, op_y1, op_x2, op_y2)
        cv2.rectangle(img_display, (op_x1, op_y1), (op_x2, op_y2), (30, 58, 138), -1)
        cv2.rectangle(img_display, (op_x1, op_y1), (op_x2, op_y2), (96, 165, 250), 1)
        cv2.putText(img_display, "Abrir (O)", (op_x1 + 12, op_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

        # Botão: Ferramenta Mão (inativo visualmente em standby)
        hp_x1, hp_y1, hp_x2, hp_y2 = w - 850, 8, w - 735, 42
        BTN_HAND_PAN = (0, 0, 0, 0)
        BTN_ZOOM_IN = (0, 0, 0, 0)
        BTN_ZOOM_OUT = (0, 0, 0, 0)
        BTN_RESET_ZOOM = (0, 0, 0, 0)
        BTN_UNDO = (0, 0, 0, 0)
        BTN_SAVE = (0, 0, 0, 0)
        cv2.rectangle(img_display, (hp_x1, hp_y1), (hp_x2, hp_y2), (30, 41, 59), -1)
        cv2.rectangle(img_display, (hp_x1, hp_y1), (hp_x2, hp_y2), (71, 85, 105), 1)
        cv2.putText(img_display, "Mao (H)", (hp_x1 + 14, hp_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (100, 116, 139), 1, cv2.LINE_AA)

        # Botão: Sair do Aplicativo (Standby)
        ex_x1, ex_y1, ex_x2, ex_y2 = w - 200, 8, w - 65, 42
        BTN_FINISH = (ex_x1, ex_y1, ex_x2, ex_y2)
        cv2.rectangle(img_display, (ex_x1, ex_y1), (ex_x2, ex_y2), (40, 40, 70), -1)
        cv2.rectangle(img_display, (ex_x1, ex_y1), (ex_x2, ex_y2), (248, 113, 113), 1)
        cv2.putText(img_display, "X Sair", (ex_x1 + 35, ex_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2, cv2.LINE_AA)

        # Mensagem central
        cv2.putText(img_display, "ANOTADOR DE MULTIDOES - IPPUC / RGBTCC", (w // 2 - 320, screen_h // 2 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img_display, "Nenhuma imagem selecionada no momento.", (w // 2 - 220, screen_h // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (148, 163, 184), 1, cv2.LINE_AA)
        cv2.putText(img_display, "Clique no botao [ Abrir (O) ] acima para escolher uma foto no seu computador.", (w // 2 - 380, screen_h // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (56, 189, 248), 1, cv2.LINE_AA)

        if modal_confirmacao_ativo:
            desenhar_modal_confirmacao(img_display)

        cv2.imshow(WINDOW_NAME, img_display)
        return

    calcular_roi()

    h_orig, w_orig = img_base.shape[:2]

    rx1, ry1 = int(round(roi_x1)), int(round(roi_y1))
    rx2, ry2 = int(round(roi_x2)), int(round(roi_y2))
    crop = img_base[ry1:ry2, rx1:rx2]

    crop_h, crop_w = crop.shape[:2]
    scale_fit = min(avail_w / max(1, crop_w), avail_h / max(1, crop_h))
    fit_w = int(round(crop_w * scale_fit))
    fit_h = int(round(crop_h * scale_fit))

    offset_x = (avail_w - fit_w) // 2
    offset_y = (avail_h - fit_h) // 2

    # Canvas principal escuro
    img_display = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
    img_display[:] = (18, 22, 30)

    # Redimensionamento nítido
    interp = cv2.INTER_LINEAR if zoom_level > 2.0 else cv2.INTER_AREA
    crop_disp = cv2.resize(crop, (fit_w, fit_h), interpolation=interp)
    img_display[offset_y:offset_y + fit_h, offset_x:offset_x + fit_w] = crop_disp

    # Moldura sutil
    cv2.rectangle(
        img_display,
        (offset_x - 1, offset_y - 1),
        (offset_x + fit_w, offset_y + fit_h),
        (51, 65, 85),
        1,
    )

    # 1. Desenha os pontos anotados que caem dentro da ROI visível
    for pt in coordenadas:
        px, py = pt["x"], pt["y"]
        if roi_x1 <= px <= roi_x2 and roi_y1 <= py <= roi_y2:
            norm_x = (px - roi_x1) / (roi_x2 - roi_x1)
            norm_y = (py - roi_y1) / (roi_y2 - roi_y1)
            disp_x = int(round(offset_x + norm_x * fit_w))
            disp_y = int(round(offset_y + norm_y * fit_h))

            if raio_marcador_display <= 1:
                cv2.circle(img_display, (disp_x, disp_y), 1, (0, 0, 255), -1)
            else:
                cv2.circle(img_display, (disp_x, disp_y), raio_marcador_display, (0, 0, 255), -1)
                cv2.circle(img_display, (disp_x, disp_y), raio_marcador_display + 1, (0, 255, 255), 1)

    # 2. Mini-Mapa PiP (Picture-in-Picture) no canto inferior direito quando ampliado
    if zoom_level > 1.05 and img_thumb is not None:
        th_h, th_w = img_thumb.shape[:2]
        pip_x = screen_w - th_w - 20
        pip_y = screen_h - th_h - 20
        img_display[pip_y:pip_y + th_h, pip_x:pip_x + th_w] = img_thumb
        cv2.rectangle(img_display, (pip_x - 1, pip_y - 1), (pip_x + th_w, pip_y + th_h), (200, 200, 200), 1)

        rect_x1 = pip_x + int(round(roi_x1 / w_orig * th_w))
        rect_y1 = pip_y + int(round(roi_y1 / h_orig * th_h))
        rect_x2 = pip_x + int(round(roi_x2 / w_orig * th_w))
        rect_y2 = pip_y + int(round(roi_y2 / h_orig * th_h))
        cv2.rectangle(img_display, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 255, 255), 2)

    # 3. Barra de HUD superior (Overlay translúcido flutuante sobre a imagem)
    hud_overlay = img_display.copy()
    cv2.rectangle(hud_overlay, (0, 0), (w, HUD_HEIGHT), (15, 23, 42), -1)
    cv2.addWeighted(hud_overlay, 0.82, img_display, 0.18, 0, img_display)
    cv2.line(img_display, (0, HUD_HEIGHT), (w, HUD_HEIGHT), (56, 189, 248), 2)

    # Placar à esquerda
    cv2.putText(
        img_display,
        f"Pessoas: {len(coordenadas)} | Zoom: {zoom_level:.1f}x",
        (16, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (74, 222, 128),
        2,
        cv2.LINE_AA,
    )

    # Status e orientações ao centro
    cv2.putText(
        img_display,
        status_mensagem,
        (350, 31),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        status_cor,
        1,
        cv2.LINE_AA,
    )

    # Botões interativos à direita:
    # 1. Botão: Abrir Imagem (O)
    op_x1, op_y1, op_x2, op_y2 = w - 970, 8, w - 860, 42
    BTN_OPEN_IMAGE = (op_x1, op_y1, op_x2, op_y2)
    cv2.rectangle(img_display, (op_x1, op_y1), (op_x2, op_y2), (30, 58, 138), -1)
    cv2.rectangle(img_display, (op_x1, op_y1), (op_x2, op_y2), (96, 165, 250), 1)
    cv2.putText(img_display, "Abrir (O)", (op_x1 + 12, op_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

    # 2. Botão: Ferramenta Mão / Pan (H)
    hp_x1, hp_y1, hp_x2, hp_y2 = w - 850, 8, w - 735, 42
    BTN_HAND_PAN = (hp_x1, hp_y1, hp_x2, hp_y2)
    if modo_mao_ativo:
        # Destaque de ferramenta ativa (Âmbar vibrante com borda branca reforçada)
        cv2.rectangle(img_display, (hp_x1, hp_y1), (hp_x2, hp_y2), (0, 140, 255), -1)
        cv2.rectangle(img_display, (hp_x1, hp_y1), (hp_x2, hp_y2), (255, 255, 255), 2)
        cv2.putText(img_display, "Mao ON (H)", (hp_x1 + 8, hp_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        # Estado inativo (Modo Marcador)
        cv2.rectangle(img_display, (hp_x1, hp_y1), (hp_x2, hp_y2), (30, 41, 59), -1)
        cv2.rectangle(img_display, (hp_x1, hp_y1), (hp_x2, hp_y2), (148, 163, 184), 1)
        cv2.putText(img_display, "Mao (H)", (hp_x1 + 14, hp_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (226, 232, 240), 1, cv2.LINE_AA)

    # 3. Zoom +
    z1_x1, z1_y1, z1_x2, z1_y2 = w - 725, 8, w - 685, 42
    BTN_ZOOM_IN = (z1_x1, z1_y1, z1_x2, z1_y2)
    cv2.rectangle(img_display, (z1_x1, z1_y1), (z1_x2, z1_y2), (30, 41, 59), -1)
    cv2.rectangle(img_display, (z1_x1, z1_y1), (z1_x2, z1_y2), (148, 163, 184), 1)
    cv2.putText(img_display, "+", (z1_x1 + 12, z1_y1 + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    # 4. Zoom -
    z2_x1, z2_y1, z2_x2, z2_y2 = w - 675, 8, w - 635, 42
    BTN_ZOOM_OUT = (z2_x1, z2_y1, z2_x2, z2_y2)
    cv2.rectangle(img_display, (z2_x1, z2_y1), (z2_x2, z2_y2), (30, 41, 59), -1)
    cv2.rectangle(img_display, (z2_x1, z2_y1), (z2_x2, z2_y2), (148, 163, 184), 1)
    cv2.putText(img_display, "-", (z2_x1 + 14, z2_y1 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    # 5. Reset Zoom (Fit)
    rz_x1, rz_y1, rz_x2, rz_y2 = w - 625, 8, w - 540, 42
    BTN_RESET_ZOOM = (rz_x1, rz_y1, rz_x2, rz_y2)
    cv2.rectangle(img_display, (rz_x1, rz_y1), (rz_x2, rz_y2), (30, 41, 59), -1)
    cv2.rectangle(img_display, (rz_x1, rz_y1), (rz_x2, rz_y2), (148, 163, 184), 1)
    cv2.putText(img_display, "Fit (R)", (rz_x1 + 12, rz_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

    # 6. Desfazer
    u_x1, u_y1, u_x2, u_y2 = w - 530, 8, w - 410, 42
    BTN_UNDO = (u_x1, u_y1, u_x2, u_y2)
    cv2.rectangle(img_display, (u_x1, u_y1), (u_x2, u_y2), (30, 110, 230), -1)
    cv2.rectangle(img_display, (u_x1, u_y1), (u_x2, u_y2), (255, 255, 255), 1)
    cv2.putText(img_display, "<- Desfazer", (u_x1 + 12, u_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

    # 7. Salvar Checkpoint
    s_x1, s_y1, s_x2, s_y2 = w - 400, 8, w - 245, 42
    BTN_SAVE = (s_x1, s_y1, s_x2, s_y2)
    cv2.rectangle(img_display, (s_x1, s_y1), (s_x2, s_y2), (180, 105, 14), -1)
    cv2.rectangle(img_display, (s_x1, s_y1), (s_x2, s_y2), (255, 255, 255), 1)
    cv2.putText(img_display, "Salvar (Ctrl+S)", (s_x1 + 10, s_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

    # 8. Finalizar
    f_x1, f_y1, f_x2, f_y2 = w - 235, 8, w - 65, 42
    BTN_FINISH = (f_x1, f_y1, f_x2, f_y2)
    cv2.rectangle(img_display, (f_x1, f_y1), (f_x2, f_y2), (40, 150, 60), -1)
    cv2.rectangle(img_display, (f_x1, f_y1), (f_x2, f_y2), (255, 255, 255), 1)
    cv2.putText(img_display, "V Finalizar", (f_x1 + 16, f_y1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2, cv2.LINE_AA)

    # 4. Modal de Confirmação de Saída (se ativo)
    if modal_confirmacao_ativo:
        desenhar_modal_confirmacao(img_display)

    cv2.imshow(WINDOW_NAME, img_display)


def desenhar_botao_modal(img, rect, label, bg_color, border_color, text_color=(255, 255, 255), font_scale=0.50):
    """Renderiza um botão retangular com texto perfeitamente centralizado no modal."""
    x1, y1, x2, y2 = rect
    cv2.rectangle(img, (x1, y1), (x2, y2), bg_color, -1)
    cv2.rectangle(img, (x1, y1), (x2, y2), border_color, 2)
    (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
    tx = x1 + (x2 - x1 - tw) // 2
    ty = y1 + (y2 - y1 + th) // 2
    cv2.putText(img, label, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 1, cv2.LINE_AA)


def desenhar_modal_confirmacao(img):
    """Renderiza a caixa de diálogo modal de confirmação de finalização sobre o canvas."""
    global BTN_MODAL_CONFIRMAR_SALVAR, BTN_MODAL_SAIR_SEM_SALVAR, BTN_MODAL_CANCELAR, MODAL_RECT

    # Overlay escuro semi-transparente
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (screen_w, screen_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)

    # Dimensões do card central
    modal_w = min(720, screen_w - 40)
    modal_h = 230
    mx1 = (screen_w - modal_w) // 2
    my1 = (screen_h - modal_h) // 2
    mx2 = mx1 + modal_w
    my2 = my1 + modal_h
    MODAL_RECT = (mx1, my1, mx2, my2)

    # Cores conforme estado
    if alteracoes_pendentes:
        cor_destaque = (0, 180, 250)    # Âmbar / Laranja
        cor_header_bg = (15, 23, 42)
        titulo = "[ ! ] ATENCAO: ALTERACOES NAO SALVAS"
        msg1 = f"Existem alteracoes pendentes nesta imagem ({len(coordenadas)} pontos totais)."
        msg2 = "O que deseja fazer antes de sair do anotador?"
    else:
        cor_destaque = (74, 222, 128)   # Verde Esmeralda
        cor_header_bg = (15, 23, 42)
        titulo = "[ V ] CONFIRMAR FINALIZACAO"
        msg1 = f"Todo o progresso esta salvo em disco ({len(coordenadas)} pontos anotados)."
        msg2 = "Deseja finalizar a contagem e gerar todos os relatorios entregaveis?"

    # Fundo do Card
    cv2.rectangle(img, (mx1, my1), (mx2, my2), (24, 20, 16), -1)
    cv2.rectangle(img, (mx1, my1), (mx2, my2), cor_destaque, 2)

    # Barra de Título Superior
    cv2.rectangle(img, (mx1 + 2, my1 + 2), (mx2 - 2, my1 + 45), cor_header_bg, -1)
    cv2.line(img, (mx1 + 2, my1 + 45), (mx2 - 2, my1 + 45), cor_destaque, 1)
    cv2.putText(img, titulo, (mx1 + 20, my1 + 31), cv2.FONT_HERSHEY_SIMPLEX, 0.65, cor_destaque, 2, cv2.LINE_AA)

    # Mensagens no corpo
    cv2.putText(img, msg1, (mx1 + 24, my1 + 82), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (241, 245, 249), 1, cv2.LINE_AA)
    cv2.putText(img, msg2, (mx1 + 24, my1 + 112), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (148, 163, 184), 1, cv2.LINE_AA)

    # Botões
    btn_y1 = my2 - 58
    btn_y2 = my2 - 18
    spacing = 14
    margin_x = 20
    btn_w = (modal_w - 2 * margin_x - 2 * spacing) // 3

    b1_x1 = mx1 + margin_x
    b1_x2 = b1_x1 + btn_w
    BTN_MODAL_CONFIRMAR_SALVAR = (b1_x1, btn_y1, b1_x2, btn_y2)

    b2_x1 = b1_x2 + spacing
    b2_x2 = b2_x1 + btn_w
    BTN_MODAL_SAIR_SEM_SALVAR = (b2_x1, btn_y1, b2_x2, btn_y2)

    b3_x1 = b2_x2 + spacing
    b3_x2 = mx2 - margin_x
    BTN_MODAL_CANCELAR = (b3_x1, btn_y1, b3_x2, btn_y2)

    if alteracoes_pendentes:
        # 3 Botões: [Salvar e Sair (S)] [Sair s/ Salvar (D)] [Cancelar (ESC)]
        desenhar_botao_modal(img, BTN_MODAL_CONFIRMAR_SALVAR, "Salvar e Sair (S)", (40, 150, 60), (74, 222, 128))
        desenhar_botao_modal(img, BTN_MODAL_SAIR_SEM_SALVAR, "Sair s/ Salvar (D)", (40, 40, 180), (248, 113, 113))
        desenhar_botao_modal(img, BTN_MODAL_CANCELAR, "Cancelar (ESC)", (45, 55, 72), (148, 163, 184))
    else:
        # 3 Botões: [Finalizar e Salvar (S)] [Sair do App (D)] [Cancelar (ESC)]
        desenhar_botao_modal(img, BTN_MODAL_CONFIRMAR_SALVAR, "Finalizar e Salvar (S)", (40, 150, 60), (74, 222, 128))
        desenhar_botao_modal(img, BTN_MODAL_SAIR_SEM_SALVAR, "Sair do App (D)", (40, 40, 180), (248, 113, 113))
        desenhar_botao_modal(img, BTN_MODAL_CANCELAR, "Cancelar (ESC)", (45, 55, 72), (148, 163, 184))


def abrir_modal_finalizacao():
    """Abre o modal visual de confirmação de finalização."""
    global modal_confirmacao_ativo, status_mensagem, status_cor
    if modal_confirmacao_ativo:
        return
    modal_confirmacao_ativo = True
    if alteracoes_pendentes:
        status_mensagem = "Atencao: alteracoes pendentes! Escolha uma opcao no modal."
        status_cor = (0, 180, 250)
    else:
        status_mensagem = "Confirmar finalizacao? Escolha uma opcao no modal."
        status_cor = (74, 222, 128)
    print(f"[*] Modal de finalização exibido (alterações pendentes: {alteracoes_pendentes}).")
    atualizar_canvas()


def fechar_modal_e_finalizar(salvar: bool = True):
    """Fecha o modal e define flag para encerrar a aplicação com ou sem salvamento."""
    global modal_confirmacao_ativo, salvar_ao_finalizar, deve_encerrar
    modal_confirmacao_ativo = False
    salvar_ao_finalizar = salvar
    deve_encerrar = True
    print(f"[*] Finalizando aplicação (salvar entregáveis={salvar}).")


def cancelar_modal():
    """Cancela o modal e retorna à edição normal."""
    global modal_confirmacao_ativo, status_mensagem, status_cor
    modal_confirmacao_ativo = False
    status_mensagem = "Finalizacao cancelada. Continuando anotacao..."
    status_cor = (203, 213, 225)
    print("[*] Finalização cancelada pelo usuário.")
    atualizar_canvas()


def desfazer_ultimo_ponto():
    """Remove o último ponto adicionado e atualiza a interface."""
    global coordenadas, status_mensagem, status_cor, alteracoes_pendentes
    if coordenadas:
        removido = coordenadas.pop()
        alteracoes_pendentes = True
        status_mensagem = f"Ponto #{removido['id']} desfeito ({len(coordenadas)} restantes)"
        status_cor = (147, 197, 253)
        print(f"[-] Ponto #{removido['id']} desfeito em: (x={removido['x']}, y={removido['y']}) | Restantes: {len(coordenadas)}")
        atualizar_canvas()
    else:
        status_mensagem = "Nenhum ponto para desfazer"
        status_cor = (248, 113, 113)
        print("[!] Nenhum ponto registrado para desfazer.")
        atualizar_canvas()


def callback_mouse(event, x, y, flags, param):
    """Manipula eventos do mouse: Zoom por scroll, Pan por arraste e marcação de pontos."""
    global coordenadas, deve_encerrar, status_mensagem, status_cor
    global is_dragging_pan, pan_start_screen, pan_start_center, center_x, center_y
    global modal_confirmacao_ativo, alteracoes_pendentes, modo_mao_ativo, solicitacao_abrir_imagem
    global BTN_MODAL_CONFIRMAR_SALVAR, BTN_MODAL_SAIR_SEM_SALVAR, BTN_MODAL_CANCELAR, MODAL_RECT
    global BTN_OPEN_IMAGE, BTN_HAND_PAN, BTN_ZOOM_IN, BTN_ZOOM_OUT, BTN_RESET_ZOOM, BTN_UNDO, BTN_SAVE, BTN_FINISH

    # Se o modal de confirmação estiver ativo, intercepta cliques exclusivamente no modal
    if modal_confirmacao_ativo:
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_LBUTTONUP):
            if BTN_MODAL_CONFIRMAR_SALVAR[0] <= x <= BTN_MODAL_CONFIRMAR_SALVAR[2] and BTN_MODAL_CONFIRMAR_SALVAR[1] <= y <= BTN_MODAL_CONFIRMAR_SALVAR[3]:
                fechar_modal_e_finalizar(salvar=True)
                return
            elif BTN_MODAL_SAIR_SEM_SALVAR[0] <= x <= BTN_MODAL_SAIR_SEM_SALVAR[2] and BTN_MODAL_SAIR_SEM_SALVAR[1] <= y <= BTN_MODAL_SAIR_SEM_SALVAR[3]:
                fechar_modal_e_finalizar(salvar=False)
                return
            elif BTN_MODAL_CANCELAR[0] <= x <= BTN_MODAL_CANCELAR[2] and BTN_MODAL_CANCELAR[1] <= y <= BTN_MODAL_CANCELAR[3]:
                cancelar_modal()
                return
            elif event == cv2.EVENT_LBUTTONDOWN and MODAL_RECT != (0, 0, 0, 0):
                # Backdrop click: clique fora do card central cancela o modal
                if not (MODAL_RECT[0] <= x <= MODAL_RECT[2] and MODAL_RECT[1] <= y <= MODAL_RECT[3]):
                    cancelar_modal()
                    return
        return

    # Se nenhuma imagem foi aberta ainda, permite apenas interação com HUD
    if img_base is None and y > HUD_HEIGHT:
        return

    # 1. Roda do Mouse (Zoom In / Out no cursor)
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            aplicar_zoom(1.35, x, y)
        else:
            aplicar_zoom(1.0 / 1.35, x, y)
        return

    # 2. Iniciar Pan (Botão do Meio ou Segurar Espaço + Botão Esquerdo ou Modo Mão no Botão Esquerdo)
    if event == cv2.EVENT_MBUTTONDOWN or (event == cv2.EVENT_LBUTTONDOWN and (space_is_pressed or (modo_mao_ativo and y > HUD_HEIGHT))):
        is_dragging_pan = True
        pan_start_screen = (x, y)
        pan_start_center = (center_x, center_y)
        return

    # 3. Arrastando (Pan em andamento)
    elif event == cv2.EVENT_MOUSEMOVE:
        if is_dragging_pan:
            dx = x - pan_start_screen[0]
            dy = y - pan_start_screen[1]
            if fit_w > 0 and fit_h > 0:
                delta_orig_x = (dx / fit_w) * (roi_x2 - roi_x1)
                delta_orig_y = (dy / fit_h) * (roi_y2 - roi_y1)
                center_x = pan_start_center[0] - delta_orig_x
                center_y = pan_start_center[1] - delta_orig_y
                atualizar_canvas()
            return

    # 4. Soltar Pan
    elif event == cv2.EVENT_MBUTTONUP or (event == cv2.EVENT_LBUTTONUP and is_dragging_pan):
        is_dragging_pan = False
        return

    # 5. Botão Esquerdo (Clique no HUD ou na Imagem)
    elif event == cv2.EVENT_LBUTTONDOWN:
        # Clique no HUD
        if y <= HUD_HEIGHT:
            if BTN_OPEN_IMAGE[0] <= x <= BTN_OPEN_IMAGE[2] and BTN_OPEN_IMAGE[1] <= y <= BTN_OPEN_IMAGE[3]:
                solicitacao_abrir_imagem = True
                status_mensagem = "Abrindo seletor de arquivos..."
                status_cor = (250, 204, 21)
                atualizar_canvas()
                return
            elif BTN_HAND_PAN[0] <= x <= BTN_HAND_PAN[2] and BTN_HAND_PAN[1] <= y <= BTN_HAND_PAN[3]:
                alternar_modo_mao()
                return
            elif BTN_ZOOM_IN[0] <= x <= BTN_ZOOM_IN[2] and BTN_ZOOM_IN[1] <= y <= BTN_ZOOM_IN[3]:
                aplicar_zoom(1.4)
                return
            elif BTN_ZOOM_OUT[0] <= x <= BTN_ZOOM_OUT[2] and BTN_ZOOM_OUT[1] <= y <= BTN_ZOOM_OUT[3]:
                aplicar_zoom(1.0 / 1.4)
                return
            elif BTN_RESET_ZOOM[0] <= x <= BTN_RESET_ZOOM[2] and BTN_RESET_ZOOM[1] <= y <= BTN_RESET_ZOOM[3]:
                reset_zoom()
                return
            elif BTN_UNDO[0] <= x <= BTN_UNDO[2] and BTN_UNDO[1] <= y <= BTN_UNDO[3]:
                desfazer_ultimo_ponto()
                return
            elif BTN_SAVE[0] <= x <= BTN_SAVE[2] and BTN_SAVE[1] <= y <= BTN_SAVE[3]:
                salvar_checkpoint()
                return
            elif BTN_FINISH[0] <= x <= BTN_FINISH[2] and BTN_FINISH[1] <= y <= BTN_FINISH[3]:
                print("[*] Botão 'Finalizar/Sair' acionado.")
                if img_base is None:
                    deve_encerrar = True
                else:
                    abrir_modal_finalizacao()
                return
            return

        # Clique dentro da imagem: Marcação de ponto na resolução original
        if img_base is not None and offset_x <= x < offset_x + fit_w and offset_y <= y < offset_y + fit_h:
            # Se o clique for na faixa do cabeçalho flutuante, não adiciona pontos
            if y <= HUD_HEIGHT:
                return
            # Se o Modo Mão estiver ativo, nunca marca ponto (já tratado no Iniciar Pan)
            if modo_mao_ativo:
                return

            h_orig, w_orig = img_base.shape[:2]
            norm_x = (x - offset_x) / fit_w
            norm_y = (y - offset_y) / fit_h

            orig_x = int(round(roi_x1 + norm_x * (roi_x2 - roi_x1)))
            orig_y = int(round(roi_y1 + norm_y * (roi_y2 - roi_y1)))

            orig_x = max(0, min(w_orig - 1, orig_x))
            orig_y = max(0, min(h_orig - 1, orig_y))

            novo_id = len(coordenadas) + 1
            coordenadas.append({"id": novo_id, "x": orig_x, "y": orig_y})
            alteracoes_pendentes = True
            status_mensagem = f"Ponto #{novo_id} anotado em ({orig_x}, {orig_y}) | Total: {len(coordenadas)}"
            status_cor = (203, 213, 225)
            print(f"[+] Ponto #{novo_id} anotado: Tela=({x}, {y}) -> Original=({orig_x}, {orig_y}) | Total: {len(coordenadas)}")
            atualizar_canvas()

    # 6. Botão Direito: Desfazer
    elif event == cv2.EVENT_RBUTTONDOWN:
        desfazer_ultimo_ponto()


def carregar_anotacoes(caminho_arquivo: Path, img_shape=None) -> int:
    """Carrega anotações prévias de um CSV ou JSON validando compatibilidade."""
    global coordenadas
    if not caminho_arquivo.exists():
        return 0

    try:
        if caminho_arquivo.suffix.lower() == ".json":
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            pontos = dados.get("pontos", [])
            coordenadas = [
                {"id": i + 1, "x": int(pt["x"]), "y": int(pt["y"])}
                for i, pt in enumerate(pontos)
            ]
        else:
            df = pd.read_csv(caminho_arquivo)
            if "x" in df.columns and "y" in df.columns:
                if img_shape is not None and len(df) > 0:
                    max_x, max_y = df["x"].max(), df["y"].max()
                    if img_shape[1] > 4000 and max_x < 1500 and max_y < 1200:
                        print(f"[AVISO] As coordenadas em {caminho_arquivo.name} parecem ser de imagem reduzida (<1500px).")
                        return 0

                coordenadas = [
                    {"id": i + 1, "x": int(row["x"]), "y": int(row["y"])}
                    for i, row in df.iterrows()
                ]
        return len(coordenadas)
    except Exception as e:
        print(f"[!] Falha ao ler anotações prévias de {caminho_arquivo}: {e}")
        return 0


def main():
    global img_base, img_thumb, raio_marcador_display, deve_encerrar, caminho_img_ativo, caminho_saida_ativo
    global screen_w, screen_h, is_fullscreen, status_mensagem, status_cor, space_is_pressed
    global center_x, center_y, zoom_level, modal_confirmacao_ativo, alteracoes_pendentes, salvar_ao_finalizar, modo_mao_ativo, solicitacao_abrir_imagem

    parser = argparse.ArgumentParser(
        description="Anotador Manual de Pontos (Ground Truth) para Contagem de Pessoas em Alta Resolução",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--imagem",
        type=Path,
        default=None,
        help="Caminho da imagem a ser anotada. Se omitido, busca em data/input/ ou abre seletor visual",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Diretório padrão para buscar imagens de entrada",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretório raiz de saída para salvar os dados de Ground Truth",
    )
    parser.add_argument(
        "--carregar",
        type=Path,
        default=None,
        help="Caminho específico de um CSV/JSON para carregar anotações prévias",
    )
    parser.add_argument(
        "--novo",
        action="store_true",
        help="Ignora checkpoints prévios e inicia uma nova anotação em branco",
    )
    parser.add_argument(
        "--raio",
        type=int,
        default=2,
        help="Raio em pixels do marcador desenhado na tela",
    )
    parser.add_argument(
        "--tela",
        type=str,
        default=None,
        help="Resolução da tela forçada no formato LARGURAxALTURA (ex: 1920x1080)",
    )
    parser.add_argument(
        "--janela",
        action="store_true",
        help="Abre em modo janela ao invés de tela cheia (Fullscreen)",
    )
    args = parser.parse_args()

    raio_marcador_display = args.raio
    is_fullscreen = not args.janela

    # 1. Determinação da resolução de exibição
    if args.tela:
        try:
            sw, sh = map(int, args.tela.lower().split("x"))
            screen_w, screen_h = sw, sh
        except ValueError:
            print("[!] Formato inválido para --tela. Usando detecção automática.")
            screen_w, screen_h = obter_resolucao_tela()
    else:
        screen_w, screen_h = obter_resolucao_tela()

    print(f"[*] Resolução de tela adotada: {screen_w}x{screen_h} px")

    # 2. Inicialização da Janela OpenCV
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    if is_fullscreen:
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.resizeWindow(WINDOW_NAME, screen_w, screen_h)

    cv2.setMouseCallback(WINDOW_NAME, callback_mouse)

    # 3. Localização e Carregamento da Imagem
    caminho_img = None
    if args.imagem:
        caminho_img = selecionar_imagem(args.imagem, args.input_dir)

    if caminho_img is not None and caminho_img.exists():
        carregar_imagem_no_app(caminho_img, args.saida, salvar_atual=False)
        if args.carregar:
            n_rec = carregar_anotacoes(args.carregar, img_base.shape)
            if n_rec > 0:
                print(f"[*] Carregadas {n_rec} anotações de: {args.carregar}")
                status_mensagem = f"✓ Carregadas {n_rec} anotações prévias"
                status_cor = (74, 222, 128)
                atualizar_canvas()
        elif args.novo:
            coordenadas.clear()
            status_mensagem = "Nova anotação em branco iniciada"
            atualizar_canvas()
    else:
        print("[*] Nenhuma imagem inicial selecionada. O app abrirá em modo de espera.")
        print("[*] Clique no botão [ Abrir (O) ] no topo para selecionar uma foto no seu computador.")
        status_mensagem = "Clique no botao [ Abrir (O) ] acima ou tecle 'O'"
        status_cor = (250, 204, 21)
        atualizar_canvas()

    print("\n" + "=" * 76)
    print("   ANOTADOR INICIADO EM ALTA RESOLUÇÃO COM ZOOM E PAN")
    print("=" * 76)
    print("  • BOTÃO [Abrir (O)]:      Escolher/abrir qualquer imagem do computador")
    print("  • BOTÃO [Mão (H)]:        Mover câmera livremente com clique esquerdo (sem marcar)")
    print("  • ROLAR MOUSE (Scroll):   Zoom In / Zoom Out exato no local apontado")
    print("  • BOTÃO DO MEIO ARRASTAR: Mover (Pan) suavemente pela cena")
    print("  • ESPAÇO + CLIQUE ESQ:    Mover (Pan) pela cena (estilo Photoshop/Figma)")
    print("  • TECLAS W / A / S / D:   Mover câmera (W=cima, A=esq, D=dir)")
    print("  • SETAS DO TECLADO:       Mover câmera (Cima, Baixo, Esquerda, Direita)")
    print("  • TECLA 'R' / [Fit]:      Resetar o Zoom (visão geral 100% da imagem)")
    print("  • BOTÃO ESQUERDO:         Marcar cabeça na resolução máxima com precisão")
    print("  • BOTÃO DIREITO / Ctrl+Z: Desfazer último ponto")
    print("  • BOTÃO [Salvar] (Ctrl+S):Salvar Checkpoint atual")
    print("  • BOTÃO [Finalizar] (F):  Finalizar e gerar relatórios completos (CSV/JSON)")
    print("  • TECLAS [ + ] e [ - ]:   Ajustar tamanho do ponto visual na tela")
    print("  • TECLA F11:              Alternar Tela Cheia / Modo Janela")
    print("=" * 76 + "\n")

    # Códigos de teclas unificados para Windows e Linux
    KEY_LEFT = {65361, 81, 2424832, 0x250000, 37}
    KEY_UP = {65362, 82, 2490368, 0x260000, 38}
    KEY_RIGHT = {65363, 83, 2555904, 0x270000, 39}
    KEY_DOWN = {65364, 84, 2621440, 0x280000, 40}

    step_pan = 60

    while not deve_encerrar:
        # Processa solicitação de abertura de imagem (disparada pelo botão no header)
        if solicitacao_abrir_imagem:
            solicitacao_abrir_imagem = False
            acao_selecionar_imagem_usuario()

        # Sincroniza dinamicamente resolução se houver redimensionamento de janela
        try:
            wrect = cv2.getWindowImageRect(WINDOW_NAME)
            if wrect is not None and len(wrect) >= 4:
                win_w, win_h = int(wrect[2]), int(wrect[3])
                if win_w >= 640 and win_h >= 480 and (abs(win_w - screen_w) >= 20 or abs(win_h - screen_h) >= 20):
                    screen_w, screen_h = win_w, win_h
                    atualizar_canvas()
        except Exception:
            pass

        raw_key = cv2.waitKeyEx(30)
        if raw_key == -1:
            space_is_pressed = False
            continue

        key = raw_key & 0xFF

        # Se o modal de confirmação de saída estiver ativo, processa exclusivamente suas teclas
        if modal_confirmacao_ativo:
            # Enter ou S: Salvar e Finalizar
            if raw_key in (10, 13) or key in (ord("s"), ord("S")):
                fechar_modal_e_finalizar(salvar=True)
                break
            # D ou X: Sair sem salvar / Sair do App
            elif key in (ord("d"), ord("D"), ord("x"), ord("X")):
                fechar_modal_e_finalizar(salvar=False)
                break
            # ESC ou C: Cancelar modal e voltar a anotar
            elif raw_key == 27 or key in (27, ord("c"), ord("C")):
                cancelar_modal()
            continue

        # Detecta barra de espaço para pan com o mouse
        if key == 32:
            space_is_pressed = True

        # 0. Abrir Imagem: Ctrl+O (15 / 0x0F) ou tecla 'o'/'O'
        if raw_key in (15, 0x0F) or (key in [ord("o"), ord("O")] and not space_is_pressed):
            acao_selecionar_imagem_usuario()

        # 0.1 Alternar Ferramenta Mão / Pan: 'h' / 'H', 'm' / 'M'
        elif key in [ord("h"), ord("H"), ord("m"), ord("M")] and not space_is_pressed:
            alternar_modo_mao()

        # 1. Salvar Checkpoint: Ctrl+S (19 / 0x13) ou tecla 's'/'S' (quando não for seta)
        elif raw_key in (19, 0x13) or (key in [ord("s"), ord("S")] and raw_key not in KEY_DOWN):
            salvar_checkpoint()

        # 2. Finalizar e Encerrar: 'f' / 'F', ESC (27)
        elif raw_key == 27 or key in [ord("f"), ord("F"), 27]:
            print("[*] Comando de finalização acionado.")
            if img_base is None:
                break
            abrir_modal_finalizacao()

        # 3. Desfazer: Ctrl+Z (26), 'z'/'Z', 'u'/'U', Backspace (8), Delete (127, 65535)
        elif raw_key in (26, 8, 127, 65535) or key in (26, ord("z"), ord("Z"), ord("u"), ord("U"), 8, 127):
            desfazer_ultimo_ponto()

        # 4. Zoom pelo teclado: 'i'/'I' (In), 'r'/'R' (Reset)
        elif key in [ord("i"), ord("I")]:
            aplicar_zoom(1.35)
        elif key in [ord("r"), ord("R")]:
            reset_zoom()

        # 5. Pan pelo teclado: W / Seta Cima, A / Seta Esq, D / Seta Dir, Seta Baixo
        elif key in [ord("w"), ord("W")] or raw_key in KEY_UP:
            mover_pan(0, step_pan)
        elif key in [ord("a"), ord("A")] or raw_key in KEY_LEFT:
            mover_pan(step_pan, 0)
        elif key in [ord("d"), ord("D")] or raw_key in KEY_RIGHT:
            mover_pan(-step_pan, 0)
        elif raw_key in KEY_DOWN:
            mover_pan(0, -step_pan)

        # 6. Ajustar tamanho do marcador (+ / -)
        elif raw_key in [ord("+"), ord("="), 43, 61]:
            raio_marcador_display = min(8, raio_marcador_display + 1)
            status_mensagem = f"Tamanho do ponto: {raio_marcador_display}px"
            status_cor = (147, 197, 253)
            atualizar_canvas()
        elif raw_key in [ord("-"), ord("_"), 45, 95]:
            raio_marcador_display = max(1, raio_marcador_display - 1)
            status_mensagem = f"Tamanho do ponto: {raio_marcador_display}px"
            status_cor = (147, 197, 253)
            atualizar_canvas()

        # 7. Alternar Fullscreen (F11)
        elif raw_key in (65480, 115, 122, 0x7A0000):
            is_fullscreen = not is_fullscreen
            if is_fullscreen:
                cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(WINDOW_NAME, screen_w - 100, screen_h - 100)

        # 8. Limpar marcações ('c' / 'C')
        elif key in [ord("c"), ord("C")]:
            if coordenadas:
                print("[!] Limpando todas as marcações.")
                coordenadas.clear()
                alteracoes_pendentes = True
                status_mensagem = "Todas as anotações foram limpas"
                status_cor = (248, 113, 113)
                atualizar_canvas()

    cv2.destroyAllWindows()

    if caminho_img_ativo is None or img_base is None or caminho_saida_ativo is None:
        print("[*] Aplicação encerrada sem imagem ativa.")
        return

    if not salvar_ao_finalizar:
        print("\n" + "=" * 76)
        print("   [!] APLICAÇÃO ENCERRADA SEM SALVAR ALTERAÇÕES RECENTES.")
        print("=" * 76 + "\n")
        return

    # --------------------------------------------------------------------------
    # Exportação Final dos Entregáveis (Executada ao Finalizar)
    # --------------------------------------------------------------------------
    stem = caminho_img_ativo.stem
    pasta_destino = caminho_saida_ativo
    h_orig, w_orig = img_base.shape[:2]

    p_csv_stem = pasta_destino / f"pontos_ground_truth_{stem}.csv"
    p_json_stem = pasta_destino / f"pontos_ground_truth_{stem}.json"
    p_json_aligned = pasta_destino / f"ground_truth_aligned_1280x1024_{stem}.json"
    p_json_aligned_canon = pasta_destino / "ground_truth_aligned_1280x1024.json"
    p_img = pasta_destino / f"rgb_anotada_ground_truth_{stem}.jpg"
    p_meta = pasta_destino / f"metadados_{stem}.json"
    p_meta_canon = pasta_destino / "metadados.json"

    # 1. Salvar CSV
    df = pd.DataFrame(coordenadas)
    df.to_csv(p_csv_stem, index=False)

    # 2. Salvar JSON de Pontos RAW
    telemetria_gt = {
        "status": "finalizado",
        "data_finalizacao": time.strftime("%Y-%m-%d %H:%M:%S"),
        "imagem_origem": str(caminho_img_ativo),
        "arquivo_nome": caminho_img_ativo.name,
        "resolucao_original": {
            "largura": int(img_base.shape[1]),
            "altura": int(img_base.shape[0]),
            "canais": int(img_base.shape[2]) if len(img_base.shape) > 2 else 1,
        },
        "total_pessoas_anotadas": len(coordenadas),
        "pontos": coordenadas,
    }
    with open(p_json_stem, "w", encoding="utf-8") as f:
        json.dump(telemetria_gt, f, indent=2, ensure_ascii=False)

    # 3. Salvar Imagem Anotada em Alta Resolução (Auditoria Visual)
    print("[*] Gravando imagem final anotada com os pontos na resolução original...")
    img_anotada_orig = img_base.copy()
    raio_orig = max(4, int(round(w_orig / 800)))
    for pt in coordenadas:
        cv2.circle(img_anotada_orig, (pt["x"], pt["y"]), raio_orig, (0, 0, 255), -1)
        cv2.circle(img_anotada_orig, (pt["x"], pt["y"]), raio_orig + 2, (0, 255, 255), 2)
    cv2.imwrite(str(p_img), img_anotada_orig)

    # 4. Salvar Ground Truth Projetado no Espaço de Inferência (1280x1024)
    pontos_aligned = []
    scale_x = 1280.0 / float(w_orig)
    scale_y = 1024.0 / float(h_orig)
    for pt in coordenadas:
        px = int(round(pt["x"] * scale_x))
        py = int(round(pt["y"] * scale_y))
        pontos_aligned.append({"id": pt["id"], "x": px, "y": py})

    gt_aligned_data = {
        "cena": caminho_img_ativo.stem,
        "arquivo_origem": caminho_img_ativo.name,
        "resolucao_alinhada": [1280, 1024],
        "total_pessoas_anotadas": len(pontos_aligned),
        "pontos": pontos_aligned,
    }
    for dest in (p_json_aligned, p_json_aligned_canon):
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(gt_aligned_data, f, indent=2, ensure_ascii=False)

    # 5. Salvar Metadados da Imagem Contada
    meta_info = {
        "imagem_contada": stem,
        "imagem_rgb": caminho_img_ativo.name,
        "status_anotacao": "finalizado",
        "data_finalizacao": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_pessoas_anotadas": len(coordenadas),
        "resolucao_raw": {
            "largura": int(img_base.shape[1]),
            "altura": int(img_base.shape[0]),
            "canais": int(img_base.shape[2]) if len(img_base.shape) > 2 else 1,
        },
        "resolucao_alinhada_inferencia": [1280, 1024],
        "arquivos": {
            "checkpoint": f"checkpoint_{stem}.json",
            "pontos_raw_json": p_json_stem.name,
            "pontos_raw_csv": p_csv_stem.name,
            "pontos_alinhados_json": p_json_aligned.name,
            "auditoria_visual_jpg": p_img.name,
        },
    }
    for dest in (p_meta, p_meta_canon):
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(meta_info, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 76)
    print("       CONTAGEM FINALIZADA E ENTREGÁVEIS GERADOS COM SUCESSO")
    print("=" * 76)
    print(f"  [✓] Imagem Base Utilizada:     {caminho_img_ativo.name} ({w_orig}x{h_orig} px)")
    print(f"  [✓] Total de Pessoas Anotadas: {len(coordenadas)}")
    print(f"  [✓] Tabela CSV de Coordenadas: {p_csv_stem.name}")
    print(f"  [✓] Metadados e Pontos JSON:   {p_json_stem.name}")
    print(f"  [✓] GT Alinhado (1280x1024):   {p_json_aligned.name}")
    print(f"  [✓] Metadados Ficha Técnica:   {p_meta.name}")
    print(f"  [✓] Imagem com Auditoria GT:   {p_img.name}")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
