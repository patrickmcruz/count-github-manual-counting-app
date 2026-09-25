# Walkthrough - Fase 06: Seletor de Imagens Resiliente (Fallback Terminal)

## 1. O que foi implementado
1. **Tratamento de Exceção para `tkinter`:**
   - Em distribuições Linux (como Ubuntu/Debian), o módulo `tkinter` pode não vir instalado de fábrica (dependendo de `python3-tk`). A exceção `ModuleNotFoundError: No module named 'tkinter'` foi devidamente encapsulada para não abortar a execução.
2. **Menu Interativo Enumerado no Terminal:**
   - Caso o seletor gráfico não esteja disponível e existam múltiplas fotos em `data/input/`, o app renderiza um menu claro no terminal listando todas as opções:
     ```text
     ================================================================
        IMAGENS DISPONÍVEIS NA PASTA input/
     ================================================================
       [1] DJI_0763_W.JPG
       [2] DJI_0765_W.JPG
     ================================================================
     Escolha o número da imagem [1-2] (Pressione Enter para [1]):
     ```
   - O usuário pode digitar o número ou apenas pressionar `Enter` para selecionar a primeira opção.
3. **Seleção Automática para Imagem Única:**
   - Se houver apenas uma imagem na pasta, ela continua sendo carregada instantaneamente sem nenhuma intervenção.

## 2. Evidência de Teste
O teste de simulação com múltiplas fotos foi executado em ambiente sem `tkinter`:
- O menu foi apresentado no terminal.
- A tecla `Enter` selecionou a imagem padrão com sucesso.
- Código de retorno `0` verificado.

## 3. Conclusão e Entrega
A branch `feat/fase-06-seletor-resiliente` foi incorporada a `develop` e disponibilizada na branch `main`.
