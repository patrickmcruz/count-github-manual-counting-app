# Tarefas - Fase 11: Inicialização em Standby por Padrão e Correção do Fluxo de Saída

- [x] Modificar `main()` em `app.py` para não auto-carregar imagens de `data/input/` por padrão, iniciando diretamente em Standby.
- [x] Adicionar botão `[ X Sair ]` no HUD durante o Modo Standby (`img_base is None`).
- [x] Implementar desacoplamento assíncrono da seleção de arquivos via flag `solicitacao_abrir_imagem` processada no loop de `main()`.
- [x] Adicionar `root.update()` e liberação de foco no `abrir_dialogo_arquivo()`.
- [x] Tornar o listener de cliques do modal de confirmação resiliente a `EVENT_LBUTTONDOWN` e `EVENT_LBUTTONUP`.
- [x] Adicionar cancelamento do modal por clique externo (*backdrop click*).
- [x] Desenvolver teste automatizado em `tests/test_standby_e_saida.py`.
- [x] Executar suíte completa de testes de regressão (`test_header_flutuante.py`, `test_modo_mao.py`, `test_confirmacao_finalizar.py`, `test_interoperabilidade.py`).
- [x] Atualizar documentação em `README.md` e `docs/GUIA_DO_ANOTADOR.md`.
- [x] Elaborar `walkthrough.md` com evidências.
- [ ] Promover merges no Gitflow (`feat/...` ➔ `develop` ➔ `main` [v1.5.0]).
- [ ] Sincronizar branches e tags no GitLab e GitHub.
