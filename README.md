🛒 Gerenciador de Fornecedores e Preços

O Gerenciador de Fornecedores é uma ferramenta desktop desenvolvida em Python para facilitar a vida de compradores e orçamentistas. Com ele, você transforma planilhas complexas de fornecedores em uma interface de consulta ágil, com busca inteligente, visualização de fotos e geração de orçamentos em PDF.
✨ Principais Funcionalidades

    Importação Inteligente: Carregue arquivos Excel ou CSV e mapeie as colunas de "Preço" e "Descrição" em segundos.

    Busca Avançada: Filtro tipo fuzzy que encontra produtos mesmo que você digite termos fora de ordem (ex: "Cabo USB" vira "USB Cabo").

    Consulta Visual: Clique duplo no produto para abrir instantaneamente a pesquisa de imagens no Google.

    Carrinho de Orçamento: Selecione os itens desejados e o sistema calcula o total automaticamente.

    Relatórios em PDF: Gere um documento pronto com os itens selecionados para envio a clientes ou supervisores.

🚀 Como usar
1. Versão Executável (Recomendado para usuários)

Se você não possui o Python instalado:

    Vá até a seção Releases deste repositório.

    Baixe o arquivo GerenciadorFornecedores.exe.

    Execute o programa (não requer instalação).

2. Rodando via Código (Para desenvolvedores)

Caso queira rodar o script original:

    Clone o repositório:
    Bash

git clone https://github.com/seu-usuario/gerenciador-fornecedores.git

Instale as dependências:
Bash

pip install pandas openpyxl pillow

Execute:
Bash

    python main.py

🛠️ Tecnologias

    Linguagem: Python 3.12

    Interface: Tkinter (Customizada com Temas Clam)

    Dados: Pandas

    Compilação: PyInstaller (para geração do .exe)

📌 Configurações de API (Opcional)

Para habilitar a visualização direta de miniaturas dentro do app, o sistema utiliza a API do Google. Você pode configurar as variáveis de ambiente GOOGLE_API e GOOGLE_CX no seu sistema para ativar essa função.

⭐ Gostou do projeto? Deixe uma estrela no repositório!
