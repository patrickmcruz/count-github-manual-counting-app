# Plano de Implementação - Fase 09: Modo Mão / Pan Interativo no Header

## 1. Visão Geral
Atualmente, quando o usuário está navegando com zoom, cliques na imagem acidentalmente registram contagens de pessoas.
Para solucionar definitivamente essa fricção, introduziremos a ferramenta **Modo Mão / Pan (`modo_mao_ativo`)** acionável via botão no menu superior (Header/HUD) ou tecla de atalho (`H`).

Quando o Modo Mão estiver ativado:
1. O clique e arraste com o **Botão Esquerdo** move o canvas suavemente (Pan), sem registrar nenhuma contagem de pessoa.
2. O botão no cabeçalho exibe destaque visual inequívoco (estilo ferramenta ativa, cor âmbar/laranja de alta visibilidade e badge de estado).
3. O status bar informa que a navegação manual está ativa.
4. Quando desativado (Modo Ponto/Marcador), o clique esquerdo volta a marcar cabeças normalmente.

---

## 2. Requisitos Técnicos

### 2.1 Controle de Estado e Variáveis Globais
- `modo_mao_ativo = False` (booleano, padrão desativado / Modo Marcador).
- Constante do botão no HUD: `BTN_HAND_PAN = (0, 0, 0, 0)`.
- Função `alternar_modo_mao()`:
  - Inverte o estado de `modo_mao_ativo`.
  - Atualiza mensagem de status e cor correspondente.
  - Atualiza o canvas imediatamente.

### 2.2 Botão no Header (HUD)
- Posicionar o botão `[ Mão (H) ]` no cabeçalho superior.
- Layout dinâmico:
  - **Inativo (Modo Marcador ativo):**
    - Cor de fundo: Slate escuro `(30, 41, 59)`.
    - Borda: Cinza suave `(148, 163, 184)`.
    - Texto: `"Mao (H)"` em branco.
  - **Ativo (Modo Mão ativo):**
    - Cor de fundo: Âmbar vibrante `(2, 132, 199)` ou Ciano `(220, 150, 0)`.
    - Borda: Branco brilhante `(255, 255, 255)` de espessura 2.
    - Texto: `"* Mao (H)"` ou `"Mao ON (H)"` em branco/negrito.
    - Ícone estilizado ou indicador visual de ferramenta selecionada.

### 2.3 Tratamento de Eventos no Mouse (`callback_mouse`)
- Se `modo_mao_ativo` for `True`:
  - `EVENT_LBUTTONDOWN` dentro da imagem:
    - Inicia o Pan: `is_dragging_pan = True`, registra `pan_start_screen` e `pan_start_center`.
    - **NÃO** adiciona nenhum ponto à lista `coordenadas`.
  - `EVENT_MOUSEMOVE`:
    - Continua o arrasto suave.
  - `EVENT_LBUTTONUP`:
    - Finaliza o Pan: `is_dragging_pan = False`.
- Se `modo_mao_ativo` for `False`:
  - `EVENT_LBUTTONDOWN` dentro da imagem adiciona ponto normalmente.
  - O arraste com Botão do Meio ou `Espaço + Botão Esquerdo` continua disponível como atalho auxiliar.

### 2.4 Atalho de Teclado
- Tecla `H` ou `h` alterna o modo mão (`alternar_modo_mao()`).
- Opcionalmente tecla `M` ou `m` (Mão / Mover).

### 2.5 Documentação e Testes
- Atualizar `README.md` e `docs/GUIA_DO_ANOTADOR.md`.
- Teste unitário em `tests/test_modo_mao.py`.
- Teste de interoperabilidade E2E com `tests/test_interoperabilidade.py`.
- Merge para `develop` e `main` via Gitflow.
