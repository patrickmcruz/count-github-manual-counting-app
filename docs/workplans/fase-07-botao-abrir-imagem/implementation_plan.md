# Plano de Implementação - Fase 07: Botão de Seleção de Imagens no App

## 1. Visão Geral
Adicionar um botão interativo `[ 📂 Abrir Imagem ]` diretamente na interface HUD do aplicativo, permitindo que o usuário clique a qualquer momento para abrir uma imagem de qualquer pasta do seu computador (Windows ou Linux).

## 2. Requisitos Técnicos
1. **Botão no HUD Superior (`BTN_OPEN_IMAGE`):**
   - Renderizar botão estilizado no painel superior: `[ 📂 Abrir Imagem ]` (ou atalho `Ctrl+O` / tecla `O`).
   - Mapear a área de clique do mouse correspondente no callback de eventos.
2. **Caixa de Diálogo Multiplataforma (`abrir_dialogo_arquivo`):**
   - No Windows: uso prioritário de `tkinter.filedialog` (nativo do instalador oficial).
   - No Linux: suporte hierárquico com detecção de `zenity` (GTK/GNOME) e `kdialog` (KDE), além de `tkinter`.
   - Fallback de terminal caso nenhuma interface gráfica esteja acessível.
3. **Gerenciamento de Estado ao Trocar de Imagem:**
   - Caso existam anotações ativas na imagem anterior, salvar automaticamente um checkpoint antes de trocar.
   - Carregar a nova imagem na memória com alta resolução ($8000 \times 6000$ ou qualquer tamanho).
   - Gerar a miniatura atualizada para o mini-mapa PiP.
   - Resetar os parâmetros de zoom/pan para enquadrar a nova foto.
   - Detectar e recuperar automaticamente pontos ou checkpoints prévios existentes para a nova imagem.
4. **Modo Standby (Sem Imagem Inicial):**
   - Se o usuário iniciar o app sem nenhuma foto em `data/input/`, exibir uma tela limpa de boas-vindas com instruções para clicar no botão `[ 📂 Abrir Imagem ]`, em vez de abortar o programa com erro.
