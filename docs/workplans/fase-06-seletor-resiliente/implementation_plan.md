# Plano de Implementação - Fase 06: Seletor de Imagens Resiliente (Fallback Terminal)

## 1. Visão Geral
Resolver a falha de inicialização em ambientes Linux onde o pacote de sistema `python3-tk` não está instalado por padrão. Quando o usuário executa o aplicativo em uma máquina sem `tkinter` e existem múltiplas imagens em `data/input/`, o app deve oferecer um menu interativo no terminal em vez de encerrar abruptamente.

## 2. Requisitos Técnicos
1. **Menu Interativo no Terminal:**
   - Detectar imagens em `data/input/`.
   - Se houver apenas 1 imagem: carregar automaticamente.
   - Se houver mais de uma imagem:
     - Tentar seletor visual Tkinter primeiro (ideal para Windows).
     - Em caso de indisponibilidade de Tkinter ou erro, exibir menu enumerado no terminal:
       ```text
       [*] Imagens disponíveis em data/input/:
         [1] DJI_0763_W.JPG
         [2] DJI_0765_W.JPG
       Escolha o número da imagem [1-2] (Padrão: 1):
       ```
     - Permitir que o usuário aperte `Enter` para selecionar imediatamente a primeira imagem.
2. **Entrada Manual de Caminho:**
   - Se nenhuma imagem estiver presente em `data/input/` e o Tkinter não estiver disponível, solicitar o caminho ou arrastar da imagem no terminal.
3. **Resiliência e Continuidade:**
   - O comportamento padrão no Windows (onde Tkinter é embutido no instalador do python.org) não é afetado, mas ganha um fallback sólido caso ocorra qualquer problema.
