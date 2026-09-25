# Plano de Implementação - Fase 02: Portabilidade do Core (`app.py`)

## 1. Visão Geral
Refatorar e desacoplar o script `scripts/anotar_pontos.py` do projeto original, transformando-o no aplicativo autônomo `app.py`. A ferramenta deve ser 100% agnóstica a sistema operacional, funcionando tanto em Windows quanto em Linux/macOS.

## 2. Requisitos Técnicos
1. **Detecção de Monitor Multiplataforma:**
   - Detectar resolução real da tela no Windows via `ctypes.windll.user32`.
   - Fallback gracioso com `tkinter` e `/sys/class/drm`.
2. **Seletor Gráfico de Imagens:**
   - Caso o usuário inicie o script sem argumentos (ex: via clique duplo no Windows), fornecer interface amigável para carregar a imagem:
     - Detecção automática se houver apenas uma imagem em `data/input/`.
     - Janela nativa de seleção de arquivo (`filedialog.askopenfilename`) se houver múltiplas ou nenhuma.
3. **Mapeamento de Teclado Resiliente:**
   - Compatibilidade com `cv2.waitKeyEx()` tratando diferenças de keycodes de setas e modificadores entre Windows e Linux.
4. **Preservação Rígida do Contrato de Ground Truth:**
   - Salvar na pasta `data/ground_truth/{STEM}/`:
     - `pontos_ground_truth_{STEM}.csv`
     - `pontos_ground_truth_{STEM}.json`
     - `ground_truth_aligned_1280x1024_{STEM}.json`
     - `rgb_anotada_ground_truth_{STEM}.jpg`
     - `metadados_{STEM}.json`
     - `checkpoint_{STEM}.json`
5. **Recuperação e Continuação Automática:**
   - Detectar e retomar anotações de sessões anteriores sem perder nenhum ponto.
