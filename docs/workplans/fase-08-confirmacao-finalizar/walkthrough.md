# Walkthrough - Fase 08: Verificação de Progresso Não Salvo e Confirmação de Saída

## 1. Visão Geral da Entrega
Nesta fase, aprimoramos o encerramento do **Anotador Manual de Multidões** (`app.py`), implementando uma camada de segurança ativa contra perda acidental de dados ao clicar em `[ Finalizar ]` ou teclar `F`/`ESC`.

O aplicativo agora rastreia todas as alterações não salvas (`alteracoes_pendentes`) e, ao solicitar a finalização:
1. **Com alterações pendentes:** Abre um modal em destaque âmbar alertando sobre os pontos não salvos e apresentando 3 opções:
   - `[ Salvar e Sair (S) ]` (Atalho: `S` ou `Enter`)
   - `[ Sair sem Salvar (D) ]` (Atalho: `D` ou `X`)
   - `[ Cancelar (ESC) ]` (Atalho: `ESC` ou `C`)
2. **Com todas as alterações salvas:** Abre um modal em destaque verde solicitando confirmação simples para gerar os relatórios finais entregáveis:
   - `[ Sim, Finalizar (Enter) ]` (Atalho: `Enter` ou `S`)
   - `[ Cancelar (ESC) ]` (Atalho: `ESC` ou `C`)

---

## 2. Arquitetura e Detalhes da Implementação

### 2.1 Rastreamento de Estado
- Variáveis globais de controle adicionadas:
  - `alteracoes_pendentes` (`bool`): Iniciada como `False` ao carregar a imagem ou ao salvar checkpoint com sucesso; torna-se `True` ao adicionar novo ponto, desfazer ponto ou limpar anotações.
  - `modal_confirmacao_ativo` (`bool`): Controla a exibição e a captura de eventos de mouse/teclado.
  - `salvar_ao_finalizar` (`bool`): Flag avaliada após a destruição da janela OpenCV para decidir se gera os entregáveis finais ou descarta.

### 2.2 Renderização Visual In-Canvas
- **Backdrop semi-transparente:** Escurece a cena com `cv2.addWeighted` a 65% de opacidade, focando a atenção no modal.
- **Card Centralizado:** Dimensões adaptativas centralizadas (`screen_w`, `screen_h`) com paleta moderna (Dark Slate, Borda Esmeralda / Âmbar).
- **Botões Dinâmicos e Texto Centralizado:** A função auxiliar `desenhar_botao_modal()` calcula automaticamente a largura e altura do texto Hershey, posicionando o rótulo perfeitamente no centro de cada botão.

### 2.3 Tratamento de Eventos (Mouse e Teclado)
- **Bloqueio de Fundo:** Enquanto `modal_confirmacao_ativo` for `True`, cliques e scrolls fora dos botões do modal são descartados, evitando marcações ou deslocamentos acidentais.
- **Atalhos do Teclado:** Captura exclusiva no `main()` de `Enter`, `S`, `D`, `X`, `ESC` e `C`.

---

## 3. Evidências de Testes

### 3.1 Testes Unitários do Modal (`tests/test_confirmacao_finalizar.py`)
```bash
$ python tests/test_confirmacao_finalizar.py
[*] Iniciando teste do modal de confirmação e rastreamento de alterações pendentes...
  [+] Testando adição de ponto...
  [+] Testando renderização do modal com alterações pendentes...
      Botões gerados (3 opções): Salvar=(300, 417, 517, 457), Descartar=(531, 417, 748, 457), Cancelar=(762, 417, 980, 457)
  [+] Testando salvar_checkpoint() e limpeza de alterações pendentes...
  [+] Testando renderização do modal com tudo salvo...
      Botões gerados (2 opções): Confirmar=(316, 417, 630, 457), Cancelar=(650, 417, 964, 457)
  [+] Testando desfazer_ultimo_ponto()...
[-] Ponto #1 desfeito em: (x=100, y=100) | Restantes: 0
  [+] Testando abrir_modal_finalizacao() e cancelar_modal()...
[*] Modal de finalização exibido (alterações pendentes: True).
[*] Finalização cancelada pelo usuário.
  [+] Testando fechar_modal_e_finalizar(salvar=False)...
[*] Modal de finalização exibido (alterações pendentes: True).
[*] Finalizando aplicação (salvar entregáveis=False).
  [+] Testando fechar_modal_e_finalizar(salvar=True)...
[*] Finalizando aplicação (salvar entregáveis=True).

[✓ SUCESSO] Todos os comportamentos do modal e alterações pendentes validados com sucesso!
```

### 3.2 Testes de Interoperabilidade E2E (`tests/test_interoperabilidade.py`)
```bash
$ python tests/test_interoperabilidade.py
[*] Gerando cenário sintético de teste em: data/ground_truth/DJI_TEST_001_W
[✓] Arquivos do contrato gerados com sucesso.
[*] GroundTruthEvaluator encontrou arquivo: ground_truth_aligned_1280x1024_DJI_TEST_001_W.json
[*] Pontos carregados pelo evaluator: 3
[*] Resultado da avaliação:
    - has_ground_truth: True
    - real_count: 3
    - rmse_continuous: 0.0
    - nae_continuous: 0.0

============================================================
  [✓ SUCESSO ABSOLUTO] 100% DE INTEROPERABILIDADE CONFIRMADA!
============================================================
```

---

## 4. Documentação Atualizada
- `README.md`: Seção **🛡️ Proteção contra Perda de Dados ao Finalizar** adicionada com a tabela de opções e atalhos do modal.
- `docs/GUIA_DO_ANOTADOR.md`: Adicionado item explicando o funcionamento da saída segura ao pausar ou concluir o trabalho.
