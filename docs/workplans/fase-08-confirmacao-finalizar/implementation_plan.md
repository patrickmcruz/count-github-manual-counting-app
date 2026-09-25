# Plano de Implementação - Fase 08: Verificação de Progresso Não Salvo e Confirmação de Saída

## 1. Visão Geral
Aprimorar o fluxo de encerramento da contagem (acionado pelo botão `[ Finalizar ]` ou tecla `F`/`ESC`). O aplicativo deve rastrear o estado das anotações e, caso existam alterações pendentes não salvas, alertar o usuário e solicitar confirmação com opções de salvar antes de sair, sair sem salvar ou cancelar. Se todas as alterações já estiverem salvas em checkpoint, apresentar uma confirmação simples para sair.

## 2. Requisitos Técnicos
1. **Rastreamento de Modificações (`alteracoes_pendentes`):**
   - Manter variável de controle de estado de modificações não salvas.
   - Definir como `True` ao adicionar ponto, desfazer ponto ou limpar anotações.
   - Definir como `False` ao carregar imagem ou ao salvar checkpoint com sucesso (`salvar_checkpoint()`).
2. **Modal Visual de Confirmação no Canvas:**
   - Renderizar sobreposição semi-transparente centralizada na tela com layout moderno e profissional.
   - **Caso 1: Com Alterações Não Salvas:**
     - Título de alerta: *"Atenção: Existem alterações não salvas!"*
     - Detalhe: Quantidade de pontos pendentes desde o último checkpoint.
     - Botões interativos:
       - `[ 💾 Salvar e Finalizar ]` (Atalho: `S` ou `Enter`)
       - `[ ⚠️ Sair sem Salvar ]` (Atalho: `D` ou `X`)
       - `[ ✕ Cancelar ]` (Atalho: `ESC` ou `C`)
   - **Caso 2: Progresso Já Salvo (Simples Confirmação):**
     - Título: *"Confirmar Finalização"*
     - Detalhe: *"Todo o progresso está salvo. Deseja finalizar e encerrar?"*
     - Botões interativos:
       - `[ ✓ Sim, Finalizar ]` (Atalho: `S` ou `Enter`)
       - `[ ✕ Cancelar ]` (Atalho: `ESC` ou `C`)
3. **Interação com Mouse e Teclado no Modal:**
   - Mapear as áreas de clique dos botões do modal no `callback_mouse`.
   - Capturar teclas de atalho no loop principal de eventos enquanto o modal estiver aberto, bloqueando marcações acidentais na imagem de fundo.
4. **Documentação e Atualização:**
   - Atualizar `README.md` e `GUIA_DO_ANOTADOR.md` explicando o novo comportamento de segurança do botão Finalizar.
