import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Importa as funções dos outros módulos. O carregar_dados agora precisa de um argumento.
from database import carregar_dados, ler_cabecalhos # <<< Importação de ler_cabecalhos
from imagem import mostrar_imagem, atualizar_imagem
from pdf_generator import gerar_pdf

class App:
    def __init__(self, root):
        self.API_KEY = "AIzaSyBPjZf7QCNqmA_--jFffjXnrj8uMyVPsng"
        self.CX = "334107ace2eb94082"
        self.root = root
        self.root.title("Consulta de Preços")
        self.root.minsize(1000, 600)

        # Cache de imagens
        self.cache_imagens = {}
        self.cache_miniaturas = {}

        # --- Variáveis de Dados e Estado ---
        self.df = pd.DataFrame() 
        self.caminho_arquivo = tk.StringVar()
        
        # Variáveis para os nomes das colunas (serão usadas pelos Comboboxes)
        self.nome_coluna_descricao = tk.StringVar(value="") 
        self.nome_coluna_preco = tk.StringVar(value="")
        self.colunas_disponiveis = [] # Lista de colunas encontradas
        
        # Dicionário para armazenar o preço numérico real dos itens selecionados (chave: iid, valor: preço_float)
        self.itens_selecionados_dados = {} 
        
        # --- Configuração de Estilos e Tema (Melhoria Visual) ---
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        
        # Estilo para Botões
        self.style.configure('TButton', font=('Arial', 10), padding=6, relief='flat', background='#dddddd')
        self.style.map('TButton', background=[('active', '#cccccc')])
        
        # Estilo para Treeview (Tabela)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background='#0078d7', foreground='white')
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.map('Treeview', background=[('selected', '#0078d7')], foreground=[('selected', 'white')])

        # Componentes que precisam ser referenciados (serão criados em criar_interface)
        self.combo_descricao = None
        self.combo_preco = None
        self.btn_carregar_dados = None
        
        # Construir interface
        self.criar_interface()
        
    # ---------------- Funções de Carregamento ---------------- #
    
    def buscar_arquivo(self):
        """Abre a caixa de diálogo para buscar o arquivo, armazena o caminho e inicia a análise."""
        caminho = filedialog.askopenfilename(
            title="Selecione a Planilha de Preços",
            filetypes=(
                ("Arquivos Excel", "*.xlsx *.xls"),
                ("Arquivos CSV", "*.csv"),
                ("Todos os Arquivos", "*.*")
            )
        )
        if caminho:
            self.caminho_arquivo.set(caminho)
            self.analisar_e_popular_colunas() # <<< Novo passo: Analisar e popular Comboboxes

    def analisar_e_popular_colunas(self):
        """Lê o cabeçalho do arquivo e popula os Comboboxes com as colunas encontradas."""
        caminho = self.caminho_arquivo.get()
        if not caminho:
            return

        # 1. Tenta ler os cabeçalhos
        try:
            self.colunas_disponiveis = ler_cabecalhos(caminho)
            
            if not self.colunas_disponiveis:
                messagebox.showwarning("Aviso", "Nenhuma coluna encontrada. Arquivo pode estar vazio ou corrompido.")
                self.btn_carregar_dados.config(state=tk.DISABLED)
                return

            # 2. Popula os Comboboxes
            self.combo_descricao['values'] = self.colunas_disponiveis
            self.combo_preco['values'] = self.colunas_disponiveis
            
            # 3. Tenta pré-selecionar 'Descrição' e 'Preço' (ou o primeiro da lista)
            # Tenta encontrar a coluna 'Descrição' (case-insensitive)
            desc_match = next((col for col in self.colunas_disponiveis if col.lower() == 'descrição'), None)
            preco_match = next((col for col in self.colunas_disponiveis if col.lower() == 'preço'), None)

            # Define os valores
            self.nome_coluna_descricao.set(desc_match if desc_match else self.colunas_disponiveis[0])
            self.nome_coluna_preco.set(preco_match if preco_match else self.colunas_disponiveis[0])
            
            # 4. Habilita o botão de carregar dados
            self.btn_carregar_dados.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Erro de Análise", f"Não foi possível ler o cabeçalho da planilha: {e}")
            self.colunas_disponiveis = []
            if self.combo_descricao:
                self.combo_descricao['values'] = []
                self.combo_preco['values'] = []
            if self.btn_carregar_dados:
                 self.btn_carregar_dados.config(state=tk.DISABLED)
            self.nome_coluna_descricao.set("")
            self.nome_coluna_preco.set("")


    def carregar_planilha(self):
        """Carrega o DataFrame usando o caminho, nomes de colunas e atualiza a tabela."""
        caminho = self.caminho_arquivo.get()
        descricao_col = self.nome_coluna_descricao.get().strip()
        preco_col = self.nome_coluna_preco.get().strip()
        
        if not caminho or not descricao_col or not preco_col:
            messagebox.showwarning("Aviso", "Selecione o arquivo e as colunas de Descrição e Preço.")
            return

        try:
            # Chama a função ADAPTADA no database.py com o caminho e os nomes das colunas
            self.df = carregar_dados(caminho, descricao_col, preco_col)
            messagebox.showinfo("Sucesso", f"Planilha carregada com sucesso! Total de {len(self.df)} linhas.")
            
            # Limpa o filtro existente, se houver, e exibe os dados
            self.limpar_filtro()
            self.atualizar_tabela() 

        except Exception as e:
            # Trata o erro levantado pelo database.py e exibe a mensagem
            messagebox.showerror("Erro de Carregamento", f"Não foi possível carregar a planilha: {e}")
            self.df = pd.DataFrame() 

    # ---------------- Funções principais ---------------- #
    def atualizar_tabela(self, *_):
        # Proteção: Se o DataFrame estiver vazio, limpa o grid e sai
        if self.df.empty:
            for item in self.tree_principal.get_children():
                self.tree_principal.delete(item)
            return

        for item in self.tree_principal.get_children():
            self.tree_principal.delete(item)

        filtro = self.entry_filtro.get().lower().strip()
        df_filtrado = self.df

        if filtro:
            import re
            pattern = '.*'.join(map(re.escape, filtro.split()))
            # Filtro fuzzy (busca por palavras soltas na ordem)
            df_filtrado = self.df[self.df['Descrição'].str.contains(pattern, case=False, na=False)]
        
        # Nomes das colunas usadas internamente (após renomeadas em database.py)
        COL_DESCRICAO = 'Descrição'
        COL_PRECO = 'Preço' 

        for index, row in df_filtrado.iterrows():
            # Usa 'Preço' (coluna renomeada em database.py)
            preco_num = row[COL_PRECO]
            
            # Formatação do preço para exibição em Real (R$)
            preco_formatado = f"R${preco_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") \
                    if pd.notna(preco_num) else "Preço não disponível"
                    
            # Insere a Descrição e o Preço Formatado
            self.tree_principal.insert('', 'end', 
                                       iid=index, # Usamos o index do DataFrame como iid
                                       values=(row[COL_DESCRICAO], preco_formatado))

        # Ajuste de largura da coluna (usando uma largura mínima/máxima mais segura)
        max_len = max((len(str(r[COL_DESCRICAO])) for _, r in df_filtrado.iterrows()), default=10)
        largura = min(500, max(200, max_len * 10))
        self.tree_principal.column("Descrição", anchor='w', width=largura)

    def adicionar_selecionados(self):
        for item_id in self.tree_principal.selection():
            valores = self.tree_principal.item(item_id, 'values')
            
            # Pega o preço numérico do DataFrame original, usando o iid como index
            try:
                # O item_id é o index numérico da linha no DataFrame (definido em atualizar_tabela)
                # O nome da coluna do DF é sempre 'Preço' graças ao database.py
                preco_num = self.df.loc[int(item_id), 'Preço'] 
            except KeyError:
                 messagebox.showwarning("Aviso", "Erro ao obter preço numérico (chave não encontrada no DataFrame).")
                 continue

            # Insere os valores formatados na Treeview de selecionados
            self.tree_selecionados.insert('', 'end', iid=item_id, values=valores)
            
            # SALVA o preço numérico no dicionário para cálculo e PDF
            try:
                self.itens_selecionados_dados[item_id] = float(preco_num)
            except (ValueError, TypeError):
                self.itens_selecionados_dados[item_id] = 0.0

            # Remove da Treeview Principal (para evitar duplicação)
            self.tree_principal.delete(item_id)
            
        self.calcular_total()

    def remover_selecionado(self, *_):
        for item_id in self.tree_selecionados.selection():
            valores = self.tree_selecionados.item(item_id, 'values')
            
            # Remove o item do dicionário de cálculo
            if item_id in self.itens_selecionados_dados:
                del self.itens_selecionados_dados[item_id]

            # Reinsere o item na tabela principal, caso ele exista no DF original
            original_index = int(item_id)
            if original_index in self.df.index:
                # Para reinserir no principal, precisamos do iid original, que é o index.
                self.tree_principal.insert('', 'end', iid=item_id, values=valores)
                
            self.tree_selecionados.delete(item_id)
            
        self.calcular_total()

    def limpar_filtro(self):
        self.entry_filtro.delete(0, tk.END)
        self.atualizar_tabela()

    def calcular_total(self):
        # Calcula o total usando o dicionário com os valores numéricos
        total = sum(self.itens_selecionados_dados.values())
        
        # Formatação final do total em Real (R$)
        self.label_total_valor.config(text=f"R${total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # ---------------- Função Google ---------------- #
    def abrir_google_imagens(self, event):
        """
        Abre o navegador e faz uma pesquisa no Google IMAGENS usando a descrição 
        do item selecionado, removendo caracteres especiais.
        """
        item = self.tree_principal.identify_row(event.y)
        if item:
            valores = self.tree_principal.item(item, 'values')
            descricao = valores[0]
            import webbrowser
            
            descricao_limpa = descricao.replace(" - ", " ").replace("-", " ").strip()
            query = descricao_limpa.replace(" ", "+") 
            
            url = f"https://www.google.com/search?tbm=isch&q={query}" 
            webbrowser.open(url)

    # ---------------- Interface ---------------- #
    def criar_interface(self):
        # Configura a expansão do container principal
        self.root.grid_rowconfigure(0, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)

        # --- FRAME PRINCIPAL (para envolver todo o conteúdo e imagem) ---
        self.main_container = tk.Frame(self.root, padx=15, pady=15)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        self.main_container.grid_columnconfigure(0, weight=3) # Coluna do conteúdo principal (Treeviews)
        self.main_container.grid_columnconfigure(1, weight=1) # Coluna da Imagem (para expandir horizontalmente)
        self.main_container.grid_rowconfigure(1, weight=1) # Linha das Treeviews expande


        # --- FRAME DE CONTEÚDO (Col 0: Carregamento, Filtro, Treeviews) ---
        content_frame = tk.Frame(self.main_container)
        content_frame.grid(row=0, column=0, rowspan=6, sticky="nsew", padx=(0, 15))
        
        content_frame.grid_rowconfigure(3, weight=1) # Linha da Treeview principal (era 2)
        content_frame.grid_rowconfigure(5, weight=1) # Linha da Treeview selecionados (era 4)
        content_frame.grid_columnconfigure(0, weight=1) # Coluna principal expande


        # --- NOVO FRAME DE CARREGAMENTO (Linha 0 do content_frame) ---
        frame_carregamento = tk.Frame(content_frame)
        frame_carregamento.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        frame_carregamento.columnconfigure(0, weight=1) 

        # Linha 0.0: Seleção de Arquivo (Botão Buscar Planilha agora chama a análise)
        tk.Entry(frame_carregamento, textvariable=self.caminho_arquivo, width=60, 
                 state='readonly', justify='left', bd=2, relief='sunken'
                 ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        # O command foi alterado para buscar_arquivo, que por sua vez chama analisar_e_popular_colunas
        ttk.Button(frame_carregamento, text="Buscar Planilha", command=self.buscar_arquivo).grid(row=0, column=1, padx=5)
        
        # Botão Carregar Dados (inicialmente desabilitado até a análise ser feita)
        self.btn_carregar_dados = tk.Button(frame_carregamento, text="Carregar Dados", command=self.carregar_planilha, state=tk.DISABLED)
        self.btn_carregar_dados.grid(row=0, column=2, padx=(5, 0)) 
        
        # Linha 1.0: Seleção das Colunas (Comboboxes)
        frame_colunas = tk.Frame(content_frame)
        frame_colunas.grid(row=1, column=0, pady=(5, 10), sticky="ew")
        frame_colunas.columnconfigure(1, weight=1) # Combobox Descrição expande
        frame_colunas.columnconfigure(3, weight=1) # Combobox Preço expande
        
        tk.Label(frame_colunas, text="Coluna Descrição:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.combo_descricao = ttk.Combobox(frame_colunas, textvariable=self.nome_coluna_descricao, state="readonly")
        self.combo_descricao.grid(row=0, column=1, sticky="ew", padx=5)

        tk.Label(frame_colunas, text="Coluna Preço:").grid(row=0, column=2, sticky="w", padx=(15, 5))
        self.combo_preco = ttk.Combobox(frame_colunas, textvariable=self.nome_coluna_preco, state="readonly")
        self.combo_preco.grid(row=0, column=3, sticky="ew", padx=(5, 0))
        
        
        # --- FRAME FILTRO (Linha 2 do content_frame) ---
        frame_filtro = tk.Frame(content_frame)
        frame_filtro.grid(row=2, column=0, pady=(5, 10), sticky="ew")
        frame_filtro.columnconfigure(1, weight=1) 

        tk.Label(frame_filtro, text="Digite o nome do produto:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.entry_filtro = tk.Entry(frame_filtro)
        self.entry_filtro.grid(row=0, column=1, sticky="ew", padx=5)
        self.entry_filtro.bind("<KeyRelease>", self.atualizar_tabela)

        ttk.Button(frame_filtro, text="Limpar Filtro", command=self.limpar_filtro).grid(row=0, column=2, padx=10)

        # Treeview principal (Linha 3 do content_frame)
        self.tree_principal = ttk.Treeview(content_frame, columns=("Descrição", "Preço"), style='Treeview', show="headings", selectmode="extended")
        self.tree_principal.heading("Descrição", text="Descrição")
        self.tree_principal.heading("Preço", text="Preço")
        self.tree_principal.grid(row=3, column=0, sticky="nsew")

        scroll_principal = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree_principal.yview)
        self.tree_principal.configure(yscroll=scroll_principal.set)
        scroll_principal.grid(row=3, column=0, sticky='nse', padx=(0, 0))

        self.tree_principal.column("Descrição", anchor='w', width=400)
        self.tree_principal.column("Preço", anchor='e', width=120)

        # Bindings
        self.tree_principal.bind("<ButtonRelease-1>", lambda e: mostrar_imagem(self))
        self.tree_principal.bind("<Double-1>", self.abrir_google_imagens) 

        # Botão adicionar (Linha 4 do content_frame - Centralizado)
        ttk.Button(content_frame, text="Adicionar Selecionados", command=self.adicionar_selecionados).grid(
            row=4, column=0, pady=10, padx=10, sticky="n"
        )

        # Treeview selecionados (Linha 5 do content_frame)
        self.tree_selecionados = ttk.Treeview(content_frame, columns=("Descrição", "Preço"), style='Treeview', show="headings", selectmode="browse")
        self.tree_selecionados.heading("Descrição", text="Descrição")
        self.tree_selecionados.heading("Preço", text="Preço")
        self.tree_selecionados.grid(row=5, column=0, sticky="nsew")

        scroll_sel = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree_selecionados.yview)
        self.tree_selecionados.configure(yscroll=scroll_sel.set)
        scroll_sel.grid(row=5, column=0, sticky='nse', padx=(0, 0))

        self.tree_selecionados.column("Descrição", anchor='w', width=400)
        self.tree_selecionados.column("Preço", anchor='e', width=120)
        self.tree_selecionados.bind("<Double-1>", self.remover_selecionado)

        # Botão gerar PDF (Linha 6 do content_frame)
        tk.Button(content_frame, text="Gerar PDF", command=lambda: gerar_pdf(self)).grid(row=6, column=0, pady=10, padx=10, sticky="n")
        
        
        # --- TOTAL (Linha 7 do content_frame) ---
        frame_total = tk.Frame(content_frame)
        frame_total.grid(row=7, column=0, pady=(5, 0), sticky="w")

        tk.Label(frame_total, text="Total:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky="w")
        self.label_total_valor = tk.Label(frame_total, text="R$0,00", font=('Arial', 12, 'bold'), fg="red")
        self.label_total_valor.grid(row=0, column=1, sticky="w", padx=(5, 0))


        # --- FRAME IMAGEM (Col 1 do main_container) ---
        frame_img = tk.Frame(self.main_container, bd=2, relief="groove")
        frame_img.grid(row=0, column=1, rowspan=8, padx=(15, 0), sticky="n")
        
        # Área de exibição da imagem
        self.label_imagem = tk.Label(frame_img, text="Imagem do produto", bg="lightgray", width=30, height=15, relief="sunken", anchor="center")
        self.label_imagem.pack(padx=10, pady=10)

        # Frame miniaturas
        self.frame_miniaturas = tk.Frame(frame_img)
        self.frame_miniaturas.pack(pady=5, padx=10)

        # Botão atualizar imagem
        ttk.Button(frame_img, text="Atualizar Imagem", command=lambda: atualizar_imagem(self)).pack(pady=5, padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()