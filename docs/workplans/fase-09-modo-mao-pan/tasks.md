# Tarefas - Fase 09: Modo Mão / Pan Interativo no Header

- [x] Declarar `modo_mao_ativo = False` e `BTN_HAND_PAN` em `app.py`.
- [x] Implementar a função `alternar_modo_mao()` para gerenciar o toggle e feedback visual.
- [x] Renderizar o botão `[ Mão (H) ]` dinamicamente no HUD em `atualizar_canvas()`, com destaque visual quando ativo.
- [x] Ajustar `callback_mouse()` para interceptar o clique no botão `BTN_HAND_PAN`.
- [x] Ajustar `callback_mouse()` para iniciar e processar o Pan no clique esquerdo quando `modo_mao_ativo == True`, impedindo marcação de pontos.
- [x] Mapear teclas `H` / `h` (e `M` / `m`) no loop do `main()` para alternar a ferramenta.
- [x] Desenvolver teste automatizado em `tests/test_modo_mao.py` verificando a prevenção de contagem acidental no modo mão.
- [x] Executar suíte de interoperabilidade `tests/test_interoperabilidade.py`.
- [x] Atualizar `README.md` e `docs/GUIA_DO_ANOTADOR.md`.
- [x] Elaborar `walkthrough.md` com evidências.
- [x] Merge da branch `feat/fase-09-modo-mao-pan` em `develop`.
- [x] Merge da branch `develop` em `main`.
