# Protocolo de Anotação e Distribuição das 50 Imagens

Este documento estabelece o procedimento operacional padrão para a divisão das 50 novas imagens de drones entre a equipe de colaboradores.

---

## 1. Organização dos Lotes

As 50 imagens podem ser distribuídas em lotes equilibrados (exemplo: 5 lotes de 10 imagens ou 10 lotes de 5 imagens, dependendo do número de colegas voluntários).

| Lote | Faixa de Imagens | Responsável | Status | Total Anotado |
| :---: | :---: | :---: | :---: | :---: |
| **Lote 01** | Imagens 01 a 10 | *A definir* | Pendente | - |
| **Lote 02** | Imagens 11 a 20 | *A definir* | Pendente | - |
| **Lote 03** | Imagens 21 a 30 | *A definir* | Pendente | - |
| **Lote 04** | Imagens 31 a 40 | *A definir* | Pendente | - |
| **Lote 05** | Imagens 41 a 50 | *A definir* | Pendente | - |

---

## 2. Fluxo de Trabalho do Coordenador

1. **Preparação do Pacote para os Anotadores:**
   - **Opção A (Recomendada - Executável .exe Portável):**  
     O coordenador executa `build_executavel_windows.bat` para gerar o `ContagemMultidoes.exe` em `dist\`. Em seguida, copia as fotos atribuídas ao colega para `dist\data\input\`, compacta a pasta `dist` como `Lote_XX.zip` e envia. **O colega não precisa instalar o Python nem configurar nada.**
   - **Opção B (Via Script e Python Instalado):**  
     O coordenador cria uma cópia zipada do repositório `count-github-manual-counting-app`, coloca as fotos em `data/input/` e envia. O colega inicia pelo arquivo `iniciar_windows.bat` (requer Python instalado).

2. **Recepção dos Dados Anotados:**
   - O colega finaliza a contagem e envia a pasta `data/ground_truth/` gerada.
   - O coordenador abre o arquivo `rgb_anotada_ground_truth_*.jpg` de cada imagem para uma auditoria visual rápida da cobertura dos pontos.

3. **Consolidação no Repositório Principal (`count-github-def_rgbtcc`):**
   - O coordenador copia as pastas validadas diretamente para a pasta oficial do pipeline:
     ```bash
     cp -r data/ground_truth/* /caminho/count-github-def_rgbtcc/data/ground_truth/
     ```
   - O pipeline e as métricas do modelo neural (`GroundTruthEvaluator` / `rgbtcc count`) reconhecerão os novos dados instantaneamente.
