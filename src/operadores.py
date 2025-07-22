# operadores.py
import tkinter as tk
from tkinter import ttk, messagebox
import banco

class JanelaOperadores(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gerenciar Operadores")
        self.geometry("600x450")
        self.configure(bg="#f0f0f0")

        self.criar_widgets()
        self.carregar_operadores()

    def criar_widgets(self):
        # --- Frame de Cadastro ---
        frame_cadastro = ttk.LabelFrame(self, text="Novo Operador", padding=10)
        frame_cadastro.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome = ttk.Entry(frame_cadastro, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_cadastro, text="Senha:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_senha = ttk.Entry(frame_cadastro, width=30, show="*")
        self.entry_senha.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_cadastro, text="Nível de Acesso:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_nivel = ttk.Combobox(frame_cadastro, values=['Admin', 'Operador'], state="readonly")
        self.combo_nivel.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.combo_nivel.set('Operador')

        btn_adicionar = ttk.Button(frame_cadastro, text="Adicionar", command=self.adicionar_operador)
        btn_adicionar.grid(row=3, column=1, padx=5, pady=10, sticky="e")

        # --- Treeview para listar operadores ---
        frame_lista = ttk.Frame(self)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        colunas = ("id", "nome", "nivel")
        self.tree_operadores = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        self.tree_operadores.heading("id", text="ID")
        self.tree_operadores.heading("nome", text="Nome")
        self.tree_operadores.heading("nivel", text="Nível de Acesso")

        self.tree_operadores.column("id", width=50, anchor="center")
        self.tree_operadores.column("nome", width=250)
        self.tree_operadores.column("nivel", width=150)

        self.tree_operadores.pack(fill="both", expand=True)

    def carregar_operadores(self):
        for i in self.tree_operadores.get_children():
            self.tree_operadores.delete(i)
        
        operadores = banco.listar_operadores()
        for op in operadores:
            self.tree_operadores.insert("", "end", values=op)

    def adicionar_operador(self):
        nome = self.entry_nome.get().strip()
        senha = self.entry_senha.get().strip()
        nivel = self.combo_nivel.get()

        if not nome or not senha:
            messagebox.showwarning("Campos Vazios", "Nome e Senha são obrigatórios.")
            return
        
        if banco.adicionar_operador(nome, senha, nivel):
            self.entry_nome.delete(0, tk.END)
            self.entry_senha.delete(0, tk.END)
            self.carregar_operadores()
