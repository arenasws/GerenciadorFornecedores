# Sys_Gerenciador_Tabela_Fornecedores
Sistema de consulta de preços de fornecedores com interface Tkinter.
- Filtra produtos por descrição.
- Seleciona itens e calcula total.
- Mostra imagens do Google.
- Gera PDF com itens selecionados.

## Como rodar
1. Instalar python no Sistema Operacional e tkinter, interface grafica do python.

a) Windows, instalador python → Marcar ""tcl/tk""."
b) macOS, Depende do método, apos instalacao do python3 executar brew install python-tk (se usar Homebrew).
Linux, apos instalar python3, rodar sudo apt install python3-tk.
2. Instale dependências: `pip install -r requirements.txt`
3. Execute `main.py`.
4. Selecionar o arquivo Excel `*.xlsx` na pasta de origem.
5. Buscar planilha, selecionar a coluna descrição e preço, carregar planilha.
*IMPORTANTE: A PLANILHA DEVE TER O TITULO DAS COLUNAS NA LINHA 1.

