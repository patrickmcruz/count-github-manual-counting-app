# Contagem Manual de Multidões

Aplicação desktop para anotação manual de pessoas em imagens aéreas e geração de dados de referência (*Ground Truth*) para os modelos de contagem do projeto DEF-RGBTCC / IPPUC.

Este README é direcionado a desenvolvedores que irão executar, testar, modificar e empacotar a aplicação. As instruções operacionais para anotadores estão em [docs/GUIA_DO_ANOTADOR.md](docs/GUIA_DO_ANOTADOR.md).

## Visão geral

A aplicação é construída em Python e usa OpenCV para renderizar a interface e receber eventos de mouse/teclado. O fluxo principal é:

1. iniciar em modo de espera, sem carregar imagens automaticamente;
2. selecionar uma imagem pelo botão central, pelo botão `Abrir (O)` ou pelo atalho `O` / `Ctrl+O`;
3. navegar pela imagem com zoom e pan;
4. registrar pontos nas pessoas;
5. salvar checkpoints e, ao finalizar, gerar os arquivos oficiais de Ground Truth.

O programa suporta imagens de alta resolução e trabalha com coordenadas na resolução original, mesmo quando a imagem é redimensionada para a tela.

## Requisitos de desenvolvimento

- Windows, Linux ou macOS;
- Python 3.9 a 3.13;
- `pip` e `venv` disponíveis;
- Tkinter instalado para o seletor nativo de arquivos;
- dependências de `requirements.txt`;
- PyInstaller apenas para gerar a distribuição Windows.

As dependências principais são:

- `opencv-python`: janela, renderização, eventos e leitura das imagens;
- `numpy`: operações matriciais e manipulação dos frames;
- `pandas`: leitura e escrita de CSV.

## Configuração do ambiente local

Na raiz do repositório, crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Também existem scripts de inicialização que automatizam a criação do ambiente e a instalação das dependências:

- Windows: `iniciar_windows.bat`;
- Linux/macOS: `iniciar_linux.sh`.

## Executar durante o desenvolvimento

Execução padrão, iniciando em standby:

```powershell
.venv\Scripts\python.exe app.py
```

Execução em uma janela de tamanho definido, útil para testes:

```powershell
.venv\Scripts\python.exe app.py --tela 1280x720 --janela
```

Opções importantes:

```text
--imagem CAMINHO       carrega uma imagem específica ao iniciar
--input-dir DIRETORIO  diretório padrão de entrada
--saida DIRETORIO      raiz dos arquivos Ground Truth
--carregar CAMINHO     carrega um CSV/JSON de anotações prévias
--novo                  ignora checkpoints anteriores
--raio N                tamanho visual do marcador
--tela LARGURAxALTURA  resolução forçada da janela
--janela                não inicia em tela cheia
```

Exemplo:

```powershell
.venv\Scripts\python.exe app.py --imagem data\input\imagem.JPG --saida data\ground_truth --janela
```

## Estrutura do projeto

```text
.
├── app.py                         # aplicação e estado da interface
├── requirements.txt               # dependências de execução
├── iniciar_windows.bat            # inicialização local no Windows
├── iniciar_linux.sh               # inicialização local no Linux/macOS
├── build_executavel_windows.bat   # build do pacote Windows com PyInstaller
├── ContagemMultidoes.spec         # configuração manual/referência do PyInstaller
├── data/
│   ├── input/                     # imagens de trabalho no ambiente de desenvolvimento
│   └── ground_truth/              # checkpoints e resultados locais
├── dist/                          # artefatos gerados para distribuição
├── build/                         # arquivos temporários do PyInstaller
├── tests/                         # testes executáveis de regressão
└── docs/                          # documentação técnica e operacional
```

Não versionar imagens brutas, checkpoints ou resultados locais. O `.gitignore` já exclui esses arquivos em `data/`.

## Arquitetura do `app.py`

O projeto ainda é uma aplicação compacta, concentrada em `app.py`. As áreas principais são:

- resolução de caminhos e estado global da aplicação;
- `abrir_dialogo_arquivo()` e `selecionar_imagem()`: seleção de imagens com fallback Tkinter, Zenity, KDialog e terminal;
- `carregar_imagem_no_app()`: troca de imagem, criação do diretório de saída e recuperação de checkpoints;
- `atualizar_canvas()`: renderização da imagem, pontos, mini-mapa, HUD e tela de standby;
- `callback_mouse()`: botões, zoom, pan e marcação de pontos;
- funções de checkpoint e finalização: persistência de CSV/JSON e geração dos artefatos finais;
- `main()`: argumentos da linha de comando, criação da janela e loop de eventos.

Ao alterar a interface, preserve o fluxo assíncrono de abertura de arquivos: o callback do mouse deve apenas ativar `solicitacao_abrir_imagem`; o seletor é executado no loop principal. Isso evita perda de foco e eventos presos no OpenCV.

## Dados e persistência

Durante a execução via código-fonte, os caminhos padrão são:

```text
data/input/
data/ground_truth/
```

Quando o aplicativo está congelado pelo PyInstaller, `APP_ROOT` passa a ser a pasta do executável. Portanto, uma distribuição em `dist/` usa:

```text
dist/data/ground_truth/
```

Para cada imagem, os resultados ficam em `ground_truth/<nome_da_imagem>/`. Dependendo do estágio do trabalho, podem existir:

- `checkpoint_*.json`: progresso recuperável;
- `pontos_ground_truth_*.csv` e `.json`: coordenadas anotadas;
- `p2pnet_<imagem>.txt`: coordenadas no formato simples `x y`, uma pessoa por linha;
- `ground_truth_aligned_*.json`: coordenadas projetadas para o modelo;
- `rgb_anotada_ground_truth_*.jpg`: imagem para auditoria visual;
- `metadados_*.json`: resumo técnico da anotação.

O carregamento automático de checkpoints é intencional. Para começar uma anotação limpa via linha de comando, use `--novo` ou remova o checkpoint correspondente com cuidado.

## Testes

Os testes são scripts Python independentes, sem dependência obrigatória de `pytest`. Execute todos no PowerShell:

```powershell
$env:PYTHONIOENCODING = "utf-8"
Get-ChildItem tests\test_*.py | ForEach-Object {
    .venv\Scripts\python.exe $_.FullName
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

Ou execute um cenário específico:

```powershell
$env:PYTHONIOENCODING = "utf-8"
.venv\Scripts\python.exe tests\test_standby_e_saida.py
```

Os testes cobrem, entre outros pontos, standby, seleção de imagem, modal de finalização, pan, HUD e interoperabilidade dos arquivos gerados. Como a interface usa OpenCV, novos testes devem preferir `patch` em `cv2.imshow`, `cv2.waitKeyEx`, callbacks e diálogos nativos.

## Gerar o executável Windows

O build deve ser executado em Windows, na raiz do repositório:

```powershell
.\build_executavel_windows.bat
```

O script:

1. reutiliza ou cria `.venv`;
2. instala as dependências e o PyInstaller;
3. oferece os modos `onefile`, `onedir` ou ambos;
4. executa o PyInstaller a partir de `app.py`;
5. cria `data/ground_truth` vazio no pacote;
6. gera `COMO_USAR.txt`.

O script limpa os diretórios de dados dentro de `dist/` antes de preparar um novo pacote. Isso evita distribuir imagens, checkpoints ou resultados de uma anotação anterior. Ele não limpa os diretórios `data/` do ambiente de desenvolvimento.

Saídas principais:

```text
dist/ContagemMultidoes.exe             # opção 1, arquivo único
dist/ContagemMultidoes/                # opção 2, pasta portátil
dist/ContagemMultidoes_Pasta/          # opção 3, variante onedir
```

O arquivo `ContagemMultidoes.spec` permanece como referência para builds manuais e configurações avançadas. O script atual não o utiliza diretamente; ele chama `PyInstaller ... app.py` para controlar os modos `onefile` e `onedir`.

Antes de distribuir, valide o conteúdo de `dist/` e compacte o pacote correspondente. O usuário selecionará as imagens diretamente pelo diálogo do aplicativo. O usuário final não precisa instalar Python.

## Alterações e manutenção

Ao implementar uma mudança:

1. preserve os caminhos relativos e o comportamento entre execução por Python e executável congelado;
2. atualize ou crie um teste de regressão para o fluxo alterado;
3. execute os testes relevantes e `py_compile` antes do build;
4. gere novamente o executável Windows quando a alteração atingir `app.py` ou os arquivos empacotados;
5. confira se `dist/data/ground_truth` não carrega dados antigos;
6. atualize a documentação correspondente.

Para validar apenas a sintaxe:

```powershell
.venv\Scripts\python.exe -m py_compile app.py
```

## Documentação complementar

- [Guia do anotador](docs/GUIA_DO_ANOTADOR.md)
- [Protocolo de anotação de 50 imagens](docs/PROTOCOLO_ANOTACAO_50_IMGS.md)
- [Guia técnico do executável Windows](docs/GUIA_COMPILACAO_EXECUTAVEL_WINDOWS.md)
- [Planos e histórico de implementação](docs/workplans/)
