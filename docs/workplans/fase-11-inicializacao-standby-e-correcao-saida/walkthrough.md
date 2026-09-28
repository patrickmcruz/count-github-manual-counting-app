# Walkthrough - Fase 11: Inicialização em Standby por Padrão e Correção do Fluxo de Saída

## 1. Visão Geral
Nesta fase, atendemos às solicitações do usuário para:
1. **Inicialização padrão em modo Standby (sem imagem)**: O aplicativo agora abre em tela de boas-vindas limpa e aguarda que o usuário selecione voluntariamente um arquivo via botão `[ Abrir (O) ]` ou atalho do teclado. O carregamento de imagens via linha de comando (`--imagem`) continua disponível como opção.
2. **Correção do encerramento e do modal de saída após cancelamento**:
   - Diagnóstico da causa raiz: o diálogo de arquivos (`zenity` / `tkinter`) era chamado de forma síncrona dentro de `callback_mouse(EVENT_LBUTTONDOWN)`. Isso bloqueava o pipeline de eventos da biblioteca gráfica do OpenCV, perdia o `EVENT_LBUTTONUP` e deixava o foco do mouse preso/inconsistente. Ao abrir o modal de confirmação posteriormente, cliques podiam ser descartados.
   - Solução adotada: o clique no botão `[ Abrir (O) ]` agora sinaliza `solicitacao_abrir_imagem = True` e retorna imediatamente. A chamada ao seletor de arquivos é processada no loop principal (`while not deve_encerrar:`), garantindo que a fila do OpenCV continue 100% responsiva.
   - Adicionada opção universal de `[ Sair do App (D) ]` no modal de confirmação mesmo quando `alteracoes_pendentes == False`.
   - Adicionado botão direto `[ X Sair ]` na barra superior durante o modo Standby.
   - Suporte a fechamento do modal por clique externo (*backdrop click*).

---

## 2. Mudanças Implementadas

### A. Inicialização em Standby por Padrão (`app.py`)
- Em `main()`, removemos a chamada implícita a `selecionar_imagem(None, args.input_dir)` quando `--imagem` não for passado.
- O aplicativo inicia com `img_base = None`, exibindo a interface escura de espera, o status com instruções e os botões `[ Abrir (O) ]` e `[ X Sair ]`.

### B. Desacoplamento Assíncrono da Seleção de Arquivos
- Adicionada a flag global `solicitacao_abrir_imagem`.
- No clique do botão `BTN_OPEN_IMAGE` em `callback_mouse`, define `solicitacao_abrir_imagem = True` e atualiza o canvas.
- No `while not deve_encerrar:`, verifica `if solicitacao_abrir_imagem:` e invoca `acao_selecionar_imagem_usuario()` no thread principal.
- Em `abrir_dialogo_arquivo()`, adicionado `root.update()` antes de `root.destroy()` no Tkinter e `cv2.waitKey(1)` para restabelecimento do foco.

### C. Resiliência do Modal de Saída
- `desenhar_modal_confirmacao`: agora garante 3 botões em ambos os estados (com e sem pendências). Caso o usuário cancele a abertura ou já tenha salvo, ele pode clicar em `[ Sair do App (D) ]` para fechar sem gerar artefatos desnecessários.
- `callback_mouse`: captura tanto `EVENT_LBUTTONDOWN` quanto `EVENT_LBUTTONUP` no modal e suporta clique fora de `MODAL_RECT` para cancelar o modal.
- Em Standby (`img_base is None`), o botão `[ X Sair ]` aciona encerramento imediato com `deve_encerrar = True`.

---

## 3. Testes e Validação

Criada a suíte `tests/test_standby_e_saida.py` e executada juntamente com todas as suítes de regressão do projeto:

```bash
/home/patrickcruz/Git/projects/contagem-de-pessoas/count-github-def_rgbtcc/.venv/bin/python tests/test_standby_e_saida.py
/home/patrickcruz/Git/projects/contagem-de-pessoas/count-github-def_rgbtcc/.venv/bin/python tests/test_confirmacao_finalizar.py
/home/patrickcruz/Git/projects/contagem-de-pessoas/count-github-def_rgbtcc/.venv/bin/python tests/test_header_flutuante.py
/home/patrickcruz/Git/projects/contagem-de-pessoas/count-github-def_rgbtcc/.venv/bin/python tests/test_modo_mao.py
/home/patrickcruz/Git/projects/contagem-de-pessoas/count-github-def_rgbtcc/.venv/bin/python tests/test_interoperabilidade.py
```

Resultados:
- `test_standby_e_saida.py`: **100% de sucesso** (5 cenários validados).
- `test_confirmacao_finalizar.py`: **100% de sucesso**.
- `test_header_flutuante.py`: **100% de sucesso**.
- `test_modo_mao.py`: **100% de sucesso**.
- `test_interoperabilidade.py`: **100% de sucesso**.
- Repositório core `count-github-def_rgbtcc`: **100% intocado e limpo**.
