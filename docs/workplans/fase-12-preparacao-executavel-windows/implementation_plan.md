# Plano de Implementação - Fase 12: Preparação e Suporte a Executável Windows (.exe)

## 1. Motivação e Objetivos
Permitir a distribuição do aplicativo de contagem manual para usuários e colegas que não possuem o Python previamente instalado no Windows, viabilizando a geração de um executável autossuficiente (`.exe`) sem requerer configuração de ambiente manual.

## 2. Mudanças Arquiteturais
1. **Resolução Dinâmica de Diretórios (`APP_ROOT`):**
   - No modo script (`python app.py`), `APP_ROOT` é `Path(__file__).resolve().parent`.
   - No modo binário congelado PyInstaller (`sys.frozen == True`), `APP_ROOT` é `Path(sys.executable).resolve().parent`.
   - Isso garante que o executável encontre `data/input/` e salve em `data/ground_truth/` na pasta onde o `.exe` estiver alocado pelo usuário (evitando descompactação errônea no `%TEMP%`).
2. **Script de Automação de Build Local (`build_executavel_windows.bat`):**
   - Criação/atualização da `.venv` com `pyinstaller`.
   - Suporte a geração em formato **Arquivo Único** (`--onefile`) ou **Pasta Portável** (`--onedir`).
   - Geração automática da árvore `data/input` e `data/ground_truth` e do guia `COMO_USAR.txt` dentro de `dist/`.
3. **Especificação de Build (`ContagemMultidoes.spec`):**
   - Configuração declarativa de hiddenimports (`pandas`, `numpy`, `cv2`, `tkinter`).
4. **Testes Automatizados de Compatibilidade:**
   - Criação de `tests/test_compatibilidade_executavel.py` validando ambos os modos de resolução de caminho.
