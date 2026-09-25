# Walkthrough - Fase 02: Portabilidade do Core (`app.py`)

## 1. O que foi implementado
1. **`app.py` autônomo:** Construído na raiz de `count-github-manual-counting-app/`, totalmente desacoplado de bibliotecas e caminhos do projeto mestre.
2. **Detecção de Resolução Multiplataforma:**
   - Suporte nativo a Windows via `ctypes.windll.user32` com DPI-awareness.
   - Fallback neutro via `tkinter` e consulta ao subsistema DRM no Linux.
3. **Seletor Visual de Imagens:**
   - Função `selecionar_imagem()` permite detectar imagem única em `data/input/` ou abrir uma caixa de diálogo nativa de seleção de arquivo (`filedialog.askopenfilename`), essencial para uso por colegas no Windows sem terminal.
4. **Normalização de Teclado OpenCV:**
   - Tratamento explícito de teclas direcionais para códigos virtuais Windows (`2424832..2621440` / `0x25..0x28`) e Linux X11 (`65361..65364`).
   - Mapeamento robusto de `Ctrl+S`, `Ctrl+Z`, `Backspace`, `Delete` e atalhos alfanuméricos.
5. **Conformidade com o Contrato de Dados:**
   - O aplicativo salva todos os 6 arquivos padrão em `data/ground_truth/{STEM}/`, incluindo o mapeamento projetado `ground_truth_aligned_1280x1024_{STEM}.json` e a imagem com círculos para auditoria visual.

## 2. Validação
- Teste de interface CLI executado via interpretador Python:
  ```bash
  python app.py --help
  ```
  Retornou o menu de opções com todos os caminhos padronizados resolvidos dinamicamente relativos a `APP_ROOT`.

## 3. Próximos Passos
Iniciar a **Fase 03: Launchers e UX Windows**, criando `requirements.txt`, `iniciar_windows.bat` (duplo clique com setup de venv automático) e `iniciar_linux.sh`.
