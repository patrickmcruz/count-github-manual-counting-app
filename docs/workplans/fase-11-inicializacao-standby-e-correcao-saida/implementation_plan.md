# Plano de Implementação - Fase 11: Inicialização em Standby por Padrão e Correção do Fluxo de Saída

## 1. Visão Geral
Atendendo às necessidades de usabilidade reportadas:
1. **Inicialização em Modo de Espera (Standby) por Padrão:**
   - O aplicativo deve iniciar limpo, diretamente na tela de espera (*Standby*), sem carregar automaticamente fotos da pasta `data/input/` e sem disparar popups de seleção no boot (a menos que seja passado explicitamente `--imagem`).
2. **Correção do Travamento dos Botões ao Sair após Cancelar Seletor:**
   - O seletor de arquivos (`zenity` / `tkinter`) não deve ser invocado de forma bloqueante dentro do callback de eventos do mouse (`cv2.EVENT_LBUTTONDOWN`), pois isso bloqueia a thread de eventos do OpenCV e impede o processamento do evento de liberação (`EVENT_LBUTTONUP`), corrompendo o estado de captura do mouse.
   - O acionamento da seleção de arquivos deve ser desacoplado via flag e processado no loop principal (`main()`).
3. **Botão de Sair Acessível em Todos os Estados:**
   - No modo Standby, o cabeçalho superior deve exibir o botão `[ X Sair ]`, permitindo fechar o aplicativo com um clique sem confirmações desnecessárias.
   - No modal de confirmação de saída (quando há imagem carregada), os cliques devem ser tolerantes a variações de eventos do mouse (`EVENT_LBUTTONDOWN` e `EVENT_LBUTTONUP`), e o modal deve permitir cancelamento ao clicar fora do card (*backdrop click*).

---

## 2. Requisitos Técnicos

### 2.1 Inicialização Limpa em `main()`
- Se nenhum argumento `--imagem` for passado via linha de comando:
  - Não invocar `selecionar_imagem()` automaticamente no boot.
  - Iniciar diretamente em modo Standby (`img_base = None`, `caminho_img_ativo = None`).
  - Renderizar a interface de espera com instruções claras e botões operacionais.

### 2.2 Botão `[ X Sair ]` no Modo Standby
- Na tela de Standby em `atualizar_canvas()`:
  - Definir `BTN_FINISH = (w - 200, 8, w - 65, 42)` estilizado em vermelho/slate com rótulo `[ X Sair ]`.
  - No `callback_mouse`, se `img_base is None` e o usuário clicar em `BTN_FINISH`, definir `deve_encerrar = True` imediatamente.

### 2.3 Desacoplamento da Abertura de Arquivo
- Criar a flag global `solicitacao_abrir_imagem = False`.
- No `callback_mouse`, ao clicar em `BTN_OPEN_IMAGE`:
  - Apenas definir `solicitacao_abrir_imagem = True` e retornar.
- No loop principal `while not deve_encerrar:` em `main()`:
  - Se `solicitacao_abrir_imagem == True`:
    - Resetar a flag `solicitacao_abrir_imagem = False`.
    - Executar `acao_selecionar_imagem_usuario()`.

### 2.4 Foco e Limpeza no Diálogo de Arquivos
- No `abrir_dialogo_arquivo`:
  - No bloco `tkinter`: chamar `root.update()` antes de `root.destroy()` para liberar o grab modal do sistema operacional.
  - Após retorno do seletor, garantir `cv2.waitKey(1)` e restaurar propriedades de janela do OpenCV para restabelecer o foco.

### 2.5 Resiliência do Modal de Confirmação de Saída
- No `callback_mouse` sob `modal_confirmacao_ativo`:
  - Aceitar eventos em `event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_LBUTTONUP)`.
  - Se o clique ocorrer fora do retângulo do card central, acionar `cancelar_modal()`.
  - Permitir fechamento seguro mesmo após cancelamentos anteriores de seletores.

---

## 3. Plano de Testes
1. `tests/test_standby_e_saida.py`:
   - Validar que o app inicia em Standby sem imagem carregada.
   - Validar presença e funcionalidade do botão `[ X Sair ]` em Standby.
   - Validar que solicitar abrir imagem e cancelar mantém o app estável.
   - Validar que o botão `[ Sair / Finalizar ]` e os botões internos do modal continuam 100% responsivos após cancelamento do seletor.
2. Regressão com `tests/test_header_flutuante.py`, `tests/test_modo_mao.py`, `tests/test_confirmacao_finalizar.py`, `tests/test_interoperabilidade.py`.
