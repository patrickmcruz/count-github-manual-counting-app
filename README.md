# Aplicativo de Anotação Manual de Multidões (Ground Truth)

Ferramenta visual de alta performance desenvolvida para anotação precisa de cabeças em imagens aéreas de drones com altíssima resolução ($8000 \times 6000$ pixels).

O objetivo deste aplicativo é gerar a referência real (*Ground Truth*) para validação dos modelos de Inteligência Artificial de contagem de pessoas do projeto de pesquisa **DEF-RGBTCC / IPPUC**.

---

## 🚀 Como Iniciar no Windows (Passo a Passo)

### 1. Pré-requisito Único
Você só precisa ter o **Python** instalado no seu Windows:
- Caso ainda não tenha, baixe em: [python.org/downloads](https://www.python.org/downloads/)
- ⚠️ **MUITO IMPORTANTE:** Na primeira tela da instalação, marque a caixinha:  
  **`[X] Add python.exe to PATH`**

---

### 2. Como Usar em 3 Passos Simples

1. **Coloque a imagem:**  
   Copie a foto aérea que você vai anotar (arquivo `.JPG`) para a pasta:  
   👉 `data/input/`

2. **Abra o aplicativo:**  
   Dê um **duplo clique** no arquivo:  
   👉 **`iniciar_windows.bat`**  
   *(Na primeira vez ele instalará os componentes necessários automaticamente em alguns segundos).*

3. **Anote as pessoas e salve:**  
   Aproxime o zoom, marque o centro de cada cabeça e salve o seu progresso!

---

### Seleção e Arquivos
| Ação | Como Fazer |
| :--- | :--- |
| **Abrir Imagem do PC** | Clicar no botão **`[ Abrir (O) ]`** no topo OU pressionar **`Ctrl + O`** / **`O`** |

### Navegação (Zoom e Movimento)
| Ação | Como Fazer |
| :--- | :--- |
| **Aproximar / Afastar (Zoom)** | **Girar a Roda do Mouse (Scroll)** centrado onde a seta estiver |
| **Mover pela imagem (Pan)** | **Clicar e segurar a Roda do Mouse** e arrastar<br>OU segurar **ESPAÇO + Clique Esquerdo** e arrastar<br>OU usar as teclas **W, A, S, D** / **Setas do Teclado** |
| **Visão Geral (Enquadrar)** | Pressionar a tecla **`R`** ou clicar no botão **`[ Fit (R) ]`** |
| **Mini-Mapa (PiP)** | Retângulo amarelo no canto inferior direito mostra a região visível |

### Marcação e Salvamento
| Ação | Como Fazer |
| :--- | :--- |
| **Marcar Cabeça** | **Clique Esquerdo** no centro da cabeça da pessoa |
| **Desfazer Último Ponto** | **Clique com Botão Direito** OU pressione **`Ctrl + Z`** OU **`U`** |
| **Salvar Checkpoint** | Pressione **`Ctrl + S`** OU clique no botão **`[ Salvar ]`** *(Faça isso com frequência!)* |
| **Finalizar Contagem** | Pressione a tecla **`F`** OU clique no botão **`[ V Finalizar ]`** |
| **Tamanho do Marcador** | Teclas **`+`** e **`-`** para aumentar/diminuir o ponto na sua tela |
| **Tela Cheia** | Tecla **`F11`** para alternar entre tela cheia e janela |

---

## 💾 O que Fazer ao Terminar a Anotação?

Ao clicar em **Finalizar** (ou tecla `F`), o programa criará uma pasta dentro de:  
👉 `data/ground_truth/NOME_DA_SUA_IMAGEM/`

Essa pasta conterá:
- `pontos_ground_truth_*.csv` e `.json` (coordenadas brutas)
- `ground_truth_aligned_1280x1024_*.json` (projeção para o modelo neural)
- `rgb_anotada_ground_truth_*.jpg` (imagem com seus pontos desenhados para conferência)
- `metadados_*.json` (resumo técnico)

📦 **Entrega:** Basta compactar (ZIP) essa pasta gerada e enviá-la para o coordenador do projeto.

---

## 📖 Documentos Complementares
- [**Guia de Boas Práticas do Anotador**](docs/GUIA_DO_ANOTADOR.md): Critérios para pessoas sob árvores, sombras e bordas.
- [**Protocolo de Distribuição das 50 Imagens**](docs/PROTOCOLO_ANOTACAO_50_IMGS.md): Divisão de trabalho e controle de lotes.
