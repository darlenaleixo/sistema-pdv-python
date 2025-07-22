# estoque.py
import tkinter as tk
from tkinter import ttk, messagebox
import banco

class JanelaEstoque(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gerenciamento de Estoque")
        self.geometry("950x600")
        self.configure(bg="#f0f0f0")

        self.criar_widgets()
        self.carregar_produtos()

    def criar_widgets(self):
        # --- Frame de Cadastro ---
        frame_cadastro = ttk.LabelFrame(self, text="Cadastro de Produto", padding=10)
        frame_cadastro.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_cadastro, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_codigo = ttk.Entry(frame_cadastro, width=20)
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_cadastro, text="Nome:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_nome = ttk.Entry(frame_cadastro, width=40)
        self.entry_nome.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_cadastro, text="Preço (R$):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_preco = ttk.Entry(frame_cadastro, width=20)
        self.entry_preco.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_cadastro, text="Qtd/Peso (Estoque):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_quantidade = ttk.Entry(frame_cadastro, width=10)
        self.entry_quantidade.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(frame_cadastro, text="Unidade:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_unidade = ttk.Combobox(frame_cadastro, values=['un', 'kg'], state="readonly", width=7)
        self.combo_unidade.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.combo_unidade.set('un')

        ttk.Label(frame_cadastro, text="Categoria:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_categoria = ttk.Entry(frame_cadastro, width=30)
        self.entry_categoria.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # --- Frame de Botões de Ação ---
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=5, fill="x", padx=10)

        self.btn_adicionar = ttk.Button(frame_botoes, text="Adicionar", command=self.adicionar_produto)
        self.btn_adicionar.pack(side="left", padx=5)
        
        self.btn_editar = ttk.Button(frame_botoes, text="Editar", command=self.editar_produto)
        self.btn_editar.pack(side="left", padx=5)

        self.btn_excluir = ttk.Button(frame_botoes, text="Excluir", command=self.excluir_produto)
        self.btn_excluir.pack(side="left", padx=5)
        
        self.btn_limpar = ttk.Button(frame_botoes, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=5)

        self.btn_estoque_baixo = ttk.Button(frame_botoes, text="Ver Estoque Baixo (un)", command=self.mostrar_estoque_baixo)
        self.btn_estoque_baixo.pack(side="right", padx=5)

        # --- Treeview para listar produtos ---
        frame_lista = ttk.Frame(self)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        colunas = ("codigo", "nome", "preco", "quantidade", "unidade", "categoria")
        self.tree_produtos = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        self.tree_produtos.heading("codigo", text="Código")
        self.tree_produtos.heading("nome", text="Nome")
        self.tree_produtos.heading("preco", text="Preço/kg (R$)", anchor="e")
        self.tree_produtos.heading("quantidade", text="Estoque", anchor="center")
        self.tree_produtos.heading("unidade", text="Un.", anchor="center")
        self.tree_produtos.heading("categoria", text="Categoria")

        self.tree_produtos.column("codigo", width=120, stretch=tk.NO)
        self.tree_produtos.column("nome", width=300)
        self.tree_produtos.column("preco", width=100, anchor="e")
        self.tree_produtos.column("quantidade", width=80, anchor="center")
        self.tree_produtos.column("unidade", width=50, anchor="center")
        self.tree_produtos.column("categoria", width=150)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_produtos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree_produtos.bind("<<TreeviewSelect>>", self.selecionar_produto)

    def carregar_produtos(self):
        """Carrega todos os produtos do banco e exibe na Treeview."""
        for i in self.tree_produtos.get_children():
            self.tree_produtos.delete(i)
        
        produtos = banco.listar_produtos()
        for produto in produtos:
            preco_formatado = f"{produto[2]:.2f}"
            self.tree_produtos.insert("", "end", values=(produto[0], produto[1], preco_formatado, produto[3], produto[5], produto[4]))

    def adicionar_produto(self):
        codigo = self.entry_codigo.get().strip()
        nome = self.entry_nome.get().strip()
        preco_str = self.entry_preco.get().strip().replace(',', '.')
        qtd_str = self.entry_quantidade.get().strip().replace(',', '.')
        categoria = self.entry_categoria.get().strip()
        unidade = self.combo_unidade.get()

        if not all([codigo, nome, preco_str, qtd_str]):
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos obrigatórios.")
            return
        
        try:
            preco = float(preco_str)
            quantidade = float(qtd_str)
        except ValueError:
            messagebox.showerror("Erro de Formato", "Preço e Quantidade/Peso devem ser números válidos.")
            return

        banco.adicionar_produto(codigo, nome, preco, quantidade, categoria, unidade)
        self.limpar_campos()
        self.carregar_produtos()
        
    def editar_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Nenhum Produto Selecionado", "Selecione um produto da lista para editar.")
            return
        
        codigo_original = self.tree_produtos.item(selecionado[0])['values'][0]
        
        codigo = self.entry_codigo.get().strip()
        nome = self.entry_nome.get().strip()
        preco_str = self.entry_preco.get().strip().replace(',', '.')
        qtd_str = self.entry_quantidade.get().strip().replace(',', '.')
        categoria = self.entry_categoria.get().strip()
        unidade = self.combo_unidade.get()

        if not all([codigo, nome, preco_str, qtd_str]):
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos.")
            return
        
        if codigo != codigo_original:
            messagebox.showerror("Erro", "Não é permitido alterar o código do produto.")
            self.entry_codigo.delete(0, tk.END)
            self.entry_codigo.insert(0, codigo_original)
            return

        try:
            preco = float(preco_str)
            quantidade = float(qtd_str)
        except ValueError:
            messagebox.showerror("Erro de Formato", "Preço e Quantidade/Peso devem ser números válidos.")
            return

        banco.editar_produto(codigo, nome, preco, quantidade, categoria, unidade)
        self.limpar_campos()
        self.carregar_produtos()

    def excluir_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Nenhum Produto Selecionado", "Selecione um produto da lista para excluir.")
            return
        
        item = self.tree_produtos.item(selecionado[0])['values']
        codigo = item[0]
        nome = item[1]

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto '{nome}'?"):
            banco.excluir_produto(codigo)
            self.limpar_campos()
            self.carregar_produtos()

    def selecionar_produto(self, event):
        """Preenche os campos de entrada com os dados do produto selecionado."""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            return
            
        item = self.tree_produtos.item(selecionado[0])['values']
        self.limpar_campos()
        
        self.entry_codigo.insert(0, item[0])
        self.entry_nome.insert(0, item[1])
        self.entry_preco.insert(0, item[2])
        self.entry_quantidade.insert(0, item[3])
        self.combo_unidade.set(item[4])
        self.entry_categoria.insert(0, item[5])

    def limpar_campos(self):
        self.entry_codigo.delete(0, tk.END)
        self.entry_nome.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_categoria.delete(0, tk.END)
        self.combo_unidade.set('un')
        self.tree_produtos.selection_remove(self.tree_produtos.selection())

    def mostrar_estoque_baixo(self):
        JanelaEstoqueBaixo(self)

class JanelaEstoqueBaixo(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Produtos com Estoque Baixo (Unidade)")
        self.geometry("700x400")
        self.configure(bg="#fff0f0")

        ttk.Label(self, text="Produtos (unidade) com 5 ou menos itens em estoque", font=("Arial", 14, "bold")).pack(pady=10)
        
        frame_lista = ttk.Frame(self)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        colunas = ("codigo", "nome", "quantidade", "categoria")
        self.tree_estoque_baixo = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        self.tree_estoque_baixo.heading("codigo", text="Código")
        self.tree_estoque_baixo.heading("nome", text="Nome")
        self.tree_estoque_baixo.heading("quantidade", text="Qtd.", anchor="center")
        self.tree_estoque_baixo.heading("categoria", text="Categoria")

        self.tree_estoque_baixo.column("codigo", width=120, stretch=tk.NO)
        self.tree_estoque_baixo.column("nome", width=300)
        self.tree_estoque_baixo.column("quantidade", width=60, anchor="center")
        self.tree_estoque_baixo.column("categoria", width=150)
        
        self.tree_estoque_baixo.pack(fill="both", expand=True)

        self.carregar_produtos_estoque_baixo()

    def carregar_produtos_estoque_baixo(self):
        produtos = banco.buscar_produtos_estoque_baixo()
        for produto in produtos:
            self.tree_estoque_baixo.insert("", "end", values=(produto[0], produto[1], int(produto[3]), produto[4]))
