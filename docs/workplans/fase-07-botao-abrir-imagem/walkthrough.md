# Walkthrough - Fase 07: Botão de Seleção de Imagens no App

## 1. O que foi implementado
1. **Botão Interativo `[ Abrir (O) ]` no HUD:**
   - Adicionado botão destacado em azul índigo no cabeçalho superior (`BTN_OPEN_IMAGE`).
   - Clicável a qualquer momento com o mouse ou via atalho de teclado `Ctrl+O` ou tecla `O`.
2. **Diálogo Nativo Multiplataforma (`abrir_dialogo_arquivo`):**
   - No Windows: aciona a caixa nativa via `tkinter.filedialog`.
   - No Linux: detecção inteligente com fallback para `zenity` (GTK/GNOME) ou `kdialog` (KDE), contornando a ausência do pacote `python3-tk`.
3. **Gerenciamento Seguro de Transição de Imagem (`carregar_imagem_no_app`):**
   - Ao trocar de imagem, o progresso da cena anterior é salvo automaticamente em disco via `salvar_checkpoint()` antes de carregar a nova foto, impedindo perda acidental de trabalho.
   - Recalcula centros, viewports e miniatura do mini-mapa PiP.
   - Continuação automática: se a imagem escolhida já possui anotações anteriores em `data/ground_truth/{STEM}`, os pontos são restaurados automaticamente na tela.
4. **Modo Standby:**
   - Se o usuário abrir o app sem selecionar nenhuma imagem, uma tela acolhedora de boas-vindas é exibida orientando a clicar no botão `[ Abrir (O) ]` em vez de fechar o programa.

## 2. Validação
- Verificada compilação e execução de `app.py --help`.
- Bateria de testes de interoperabilidade executada com sucesso contra o projeto oficial.
- Documentação do `README.md` atualizada com o novo botão e atalho.

## 3. Conclusão e Entrega
A branch `feat/fase-07-botao-abrir-imagem` foi concluída, mesclada em `develop` e liberada na branch `main`.
