# pagamento.py
import tkinter as tk
from tkinter import ttk, messagebox
import banco

class JanelaPagamento(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gerenciar Formas de Pagamento")
        self.geometry("500x400")
        self.configure(bg="#f0f0f0")

        self.criar_widgets()
        self.carregar_formas_pagamento()

    def criar_widgets(self):
        # --- Frame de Cadastro ---
        frame_cadastro = ttk.LabelFrame(self, text="Nova Forma de Pagamento", padding=10)
        frame_cadastro.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_cadastro, text="Nome:").pack(side="left", padx=5)
        self.entry_nome = ttk.Entry(frame_cadastro, width=30)
        self.entry_nome.pack(side="left", padx=5, expand=True, fill="x")
        
        self.btn_adicionar = ttk.Button(frame_cadastro, text="Adicionar", command=self.adicionar_forma_pagamento)
        self.btn_adicionar.pack(side="left", padx=5)

        # --- Frame da Lista ---
        frame_lista = ttk.Frame(self)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        self.listbox_pagamentos = tk.Listbox(frame_lista, font=("Arial", 12))
        self.listbox_pagamentos.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.listbox_pagamentos.yview)
        self.listbox_pagamentos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # --- Botão de Excluir ---
        self.btn_excluir = ttk.Button(self, text="Excluir Selecionado", command=self.excluir_forma_pagamento)
        self.btn_excluir.pack(pady=10)

    def carregar_formas_pagamento(self):
        self.listbox_pagamentos.delete(0, tk.END)
        formas = banco.listar_formas_pagamento()
        for forma in formas:
            self.listbox_pagamentos.insert(tk.END, forma)

    def adicionar_forma_pagamento(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Campo Vazio", "Digite o nome da forma de pagamento.")
            return
        
        banco.adicionar_forma_pagamento(nome)
        self.entry_nome.delete(0, tk.END)
        self.carregar_formas_pagamento()

    def excluir_forma_pagamento(self):
        selecionado = self.listbox_pagamentos.curselection()
        if not selecionado:
            messagebox.showwarning("Nenhuma Seleção", "Selecione uma forma de pagamento para excluir.")
            return

        nome = self.listbox_pagamentos.get(selecionado[0])
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir '{nome}'?"):
            banco.excluir_forma_pagamento(nome)
            self.carregar_formas_pagamento()
