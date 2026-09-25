# Plano de Implementação - Fase 10: Header Flutuante Sobreposto (Overlay Fixo)

## 1. Visão Geral
Conforme alinhado com o usuário, o cabeçalho (HUD / Menu) do aplicativo deve **acompanhar a imagem durante qualquer nível de zoom ou deslocamento (pan)** de forma contínua e imersiva.

Para alcançar essa experiência moderna (estilo Figma, Photoshop e Miro):
1. **Ocupação Total da Tela pela Imagem (`avail_h = screen_h`):**
   - A imagem não mais fica restrita ou empurrada para baixo por uma barra preta opaca de 50px.
   - A área visível da foto agora utiliza 100% da resolução vertical e horizontal da tela, ficando perfeitamente centralizada.
2. **Header Flutuante Translúcido (Glassmorphism / Overlay Fixo):**
   - O menu superior é renderizado como uma camada translúcida suspensa sobre a imagem (`cv2.addWeighted` a ~82% de opacidade no fundo).
   - O usuário consegue perceber visualmente a continuidade da foto por baixo do cabeçalho.
   - Todos os textos, placares e botões interativos (`[ Abrir ]`, `[ Mao (H) ]`, `[ + ]`, `[ - ]`, `[ Fit ]`, `[ Desfazer ]`, `[ Salvar ]`, `[ Finalizar ]`) permanecem 100% nítidos, com cores vibrantes e sempre acessíveis a qualquer momento do zoom.
3. **Proteção de Interação e Clique:**
   - A zona do cabeçalho (`y <= HUD_HEIGHT`) atua como camada de controle: cliques nela ativam ferramentas ou funções e nunca inserem pontos de contagem na foto.

---

## 2. Requisitos Técnicos

### 2.1 Ajustes no Cálculo do Canvas (`atualizar_canvas`)
- Alterar `avail_h = screen_h` (ao invés de `screen_h - HUD_HEIGHT`).
- Centralizar o enquadramento na tela inteira:
  - `offset_y = (avail_h - fit_h) // 2`.
- Renderizar a imagem e pontos ocupando toda a tela.
- Em seguida, renderizar a faixa de cabeçalho (`y = 0` até `y = HUD_HEIGHT`) como uma sobreposição translúcida sobre a imagem:
  - `hud_overlay = img_display.copy()`
  - `cv2.rectangle(hud_overlay, (0, 0), (w, HUD_HEIGHT), (15, 23, 42), -1)`
  - `cv2.addWeighted(hud_overlay, 0.82, img_display, 0.18, 0, img_display)`
  - Linha de divisão ciano: `cv2.line(img_display, (0, HUD_HEIGHT), (w, HUD_HEIGHT), (56, 189, 248), 2)`
- Desenhar todos os botões e placares de telemetria sobre a camada mesclada.

### 2.2 Preservação e Integração no `callback_mouse`
- Manter a regra: cliques com `y <= HUD_HEIGHT` acionam exclusivamente os botões do cabeçalho.
- No modo de marcação (`modo_mao_ativo == False`), cliques em `y > HUD_HEIGHT` marcam pontos com cálculo exato de coordenadas reais.
- No modo mão (`modo_mao_ativo == True`), cliques em `y > HUD_HEIGHT` iniciam Pan livre sem marcar pontos.

### 2.3 Responsividade ao Redimensionamento de Janela
- Monitorar a resolução dinâmica da janela do OpenCV via `cv2.getWindowImageRect(WINDOW_NAME)`, atualizando `screen_w` e `screen_h` caso a janela seja redimensionada.

### 2.4 Documentação e Validação
- Testes unitários em `tests/test_header_flutuante.py`.
- Teste de regressão com `tests/test_confirmacao_finalizar.py` e `tests/test_modo_mao.py`.
- Suíte E2E de contrato em `tests/test_interoperabilidade.py`.
- Atualizar `README.md` e `docs/GUIA_DO_ANOTADOR.md`.
- Concluir merges Gitflow (`feat/fase-10-header-flutuante-overlay` ➔ `develop` ➔ `main`).
