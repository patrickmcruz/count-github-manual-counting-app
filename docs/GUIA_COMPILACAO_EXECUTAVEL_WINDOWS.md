# Guia Técnico de Compilação do Executável Windows (.exe)

Este documento orienta os desenvolvedores e coordenadores do projeto sobre como gerar e empacotar a aplicação de **Contagem Manual de Multidões** em um executável autônomo para Windows (`.exe`), eliminando a necessidade de os anotadores possuírem Python instalado em suas máquinas.

---

## 1. Pré-Requisitos para Compilação

Para compilar o executável, você precisará de uma máquina Windows com:
* **Python 3.9 a 3.13** instalado com a opção `"Add python.exe to PATH"` marcada.
* Acesso à internet na primeira execução para que o `pip` baixe o `PyInstaller` e as dependências (`opencv-python`, `numpy`, `pandas`).

> [!NOTE]
> O compilador `PyInstaller` gera binários nativos para o sistema operacional em que é executado. Por essa razão, a compilação do `.exe` do Windows deve ser disparada em uma máquina Windows (ou em uma VM / GitHub Actions Windows).

---

## 2. Como Compilar (Passo a Passo)

1. No Windows, navegue até a pasta do repositório `count-github-manual-counting-app`.
2. Dê um **duplo clique** no script:  
   👉 **`build_executavel_windows.bat`**
3. O script verificará o ambiente e apresentará o seguinte menu:
   ```text
   Escolha o formato de executável desejado:
     [1] Arquivo Único (.exe portátil de ~60MB - mais fácil de compartilhar)
     [2] Pasta Portável (Abertura instantânea sem descompactação temporária)
     [3] Compilar Ambos
   ```
4. Digite `1` ou pressione `Enter` para a opção padrão (**Arquivo Único**).
5. O processo levará entre 30 e 90 segundos. Ao final, a pasta `dist\` conterá o pacote pronto.

---

## 3. Comparativo entre os Formatos de Executável

| Característica | Arquivo Único (`--onefile`) | Pasta Portável (`--onedir`) |
| :--- | :---: | :---: |
| **Estrutura** | Um único arquivo `ContagemMultidoes.exe` | Pasta `ContagemMultidoes\` com `.exe` e DLLs |
| **Facilidade de Distribuição** | ⭐⭐⭐⭐⭐ (apenas um `.exe` e a pasta de fotos) | ⭐⭐⭐⭐ (compartilha a pasta inteira compactada em `.zip`) |
| **Tempo de Abertura Inicial** | ~2 a 3 segundos (descompacta DLLs no `%TEMP%`) | **Instantâneo (< 0.5s)** |
| **Uso de Disco Temporário** | Cria pasta temporária em `%TEMP%\_MEIxxxxxx` | Não utiliza `%TEMP%` |
| **Recomendação** | **Ideal para enviar para anotadores casuais** | **Ideal para computadores corporativos restritos** |

---

## 4. Arquitetura de Caminhos e Resolução de Diretórios

Para evitar que o executável busque fotos dentro da pasta temporária do PyInstaller (`_MEIPASS`), a aplicação utiliza a seguinte lógica em `app.py`:

```python
if getattr(sys, "frozen", False):
    # Executável compilado pelo PyInstaller (.exe)
    APP_ROOT = Path(sys.executable).resolve().parent
else:
    # Execução normal via script (.py)
    APP_ROOT = Path(__file__).resolve().parent

DEFAULT_INPUT_DIR = APP_ROOT / "data" / "input"
DEFAULT_OUTPUT_DIR = APP_ROOT / "data" / "ground_truth"
```

Isso garante que:
* A pasta do executável seja usada como referência inicial pelo seletor de imagens quando o usuário não escolher outra pasta.
* Os relatórios e checkpoints sejam gravados em: `pasta_do_executavel\data\ground_truth\`

---

## 5. Estrutura do Pacote para Entrega aos Anotadores

Após a execução do build, a pasta `dist\` gerada já estará pronta para ser compactada:

```text
dist/
├── ContagemMultidoes.exe    <- Executável principal
├── COMO_USAR.txt            <- Instruções rápidas para o anotador
└── data/
    └── ground_truth/        <- Pasta onde os relatórios finais serão gerados
```

### Como enviar para o anotador:
1. Compacte a pasta `dist` como `Lote_XX_Contagem.zip`.
2. Envie o `.zip` para o colega. **Ele só precisará extrair, abrir o `ContagemMultidoes.exe` e selecionar as imagens pelo diálogo.**

---

## 6. Avisos de Segurança do Windows Defender (SmartScreen)

Como o executável gerado não possui assinatura de certificado digital comercial paga (padrão em ferramentas acadêmicas e open-source), o **Windows SmartScreen** pode exibir a tela azul:  
*"O Windows protegeu o seu computador"*.

**Como orientar os colegas anotadores:**
1. Clicar em **"Mais informações"** (*More info*).
2. Clicar no botão **"Executar assim mesmo"** (*Run anyway*).
*(Essa confirmação só precisa ser feita na primeira vez que o executável for aberto).*
