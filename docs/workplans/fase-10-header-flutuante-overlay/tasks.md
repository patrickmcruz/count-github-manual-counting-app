# Tarefas - Fase 10: Header Flutuante Sobreposto (Overlay Fixo)

- [x] Ajustar `avail_h = screen_h` e `offset_y = (avail_h - fit_h) // 2` em `atualizar_canvas()` para que a imagem aproveite 100% da tela.
- [x] Implementar a renderização do header superior como overlay translúcido (`cv2.addWeighted`) sobre a imagem no canvas.
- [x] Manter botões e textos nítidos e legíveis sobre o fundo translúcido.
- [x] Garantir que cliques no header (`y <= HUD_HEIGHT`) ativem/desativem comportamentos sem marcar pontos, mesmo sob zoom elevado.
- [x] Suportar redimensionamento dinâmico da janela via `cv2.getWindowImageRect()`.
- [x] Desenvolver teste automatizado em `tests/test_header_flutuante.py`.
- [x] Executar suíte completa de testes (`test_confirmacao_finalizar.py`, `test_modo_mao.py`, `test_interoperabilidade.py`).
- [x] Atualizar documentação em `README.md` e `docs/GUIA_DO_ANOTADOR.md`.
- [x] Elaborar `walkthrough.md` com evidências.
- [x] Merge da branch `feat/fase-10-header-flutuante-overlay` em `develop`.
- [x] Merge da branch `develop` em `main`.
