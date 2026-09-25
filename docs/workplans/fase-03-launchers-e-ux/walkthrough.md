# Walkthrough - Fase 03: Launchers e UX Windows

## 1. O que foi implementado
1. **`requirements.txt`:** Especificação exata das versões mínimas estáveis de `opencv-python`, `numpy` e `pandas`.
2. **`iniciar_windows.bat`:**
   - Detecção automática de `python` e `py` no ambiente do Windows.
   - Mensagem amigável com link e instruções caso o Python não esteja instalado ou não esteja no PATH.
   - Criação automática do `.venv` e instalação transparente de dependências.
   - Execução direta com tratamento para evitar que o prompt feche abruptamente em caso de erro.
3. **`iniciar_linux.sh`:**
   - Script shell completo com permissão de execução `+x` para testes locais e desenvolvimento no Linux/macOS.

## 2. Validação
- Permissões verificadas no sistema de arquivos.
- Estrutura de dependências validada com os módulos importados em `app.py`.

## 3. Próximos Passos
Iniciar a **Fase 04: Documentação para os Colegas**, redigindo o `README.md` principal do repositório, o `GUIA_DO_ANOTADOR.md` e o protocolo de distribuição para as 50 imagens.
