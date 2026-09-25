# Plano de Implementação - Fase 05: Validação E2E e Interoperabilidade

## 1. Visão Geral
Validar a cadeia completa de ponta a ponta: desde a geração dos artefatos de Ground Truth pelo novo aplicativo `app.py` até o consumo desses dados pelo avaliador oficial (`GroundTruthEvaluator`) do projeto mestre `count-github-def_rgbtcc`, garantindo 100% de compatibilidade sem qualquer quebra de contrato.

## 2. Requisitos Técnicos
1. Simular uma sessão de anotação e geração de arquivos entregáveis via `app.py`.
2. Verificar a existência e consistência dos 6 arquivos de saída:
   - `pontos_ground_truth_{STEM}.csv`
   - `pontos_ground_truth_{STEM}.json`
   - `ground_truth_aligned_1280x1024_{STEM}.json`
   - `rgb_anotada_ground_truth_{STEM}.jpg`
   - `metadados_{STEM}.json`
   - `checkpoint_{STEM}.json`
3. Executar o `GroundTruthEvaluator` de `src/rgbtcc/telemetry/metrics.py` apontando para os dados gerados, comprovando que a leitura de pontos, metadados e contagem real ocorre com 100% de sucesso.
4. Concluir a fase, mesclar em `develop` e consolidar a release na branch `main`.
