# relatorios.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  # pip install tkcalendar
import banco
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class JanelaRelatorios(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Relatórios de Gestão")
        self.geometry("1000x700")
        self.configure(bg="#e8e8e8")

        self.criar_widgets()

    def criar_widgets(self):
        # --- Frame de Filtros ---
        frame_filtros = ttk.LabelFrame(self, text="Filtros", padding=10)
        frame_filtros.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_filtros, text="Data Início:").grid(row=0, column=0, padx=5, pady=5)
        self.date_inicio = DateEntry(frame_filtros, date_pattern='yyyy-mm-dd', width=12, background='darkblue',
                                     foreground='white', borderwidth=2)
        self.date_inicio.set_date(date.today() - timedelta(days=7))
        self.date_inicio.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=2, padx=5, pady=5)
        self.date_fim = DateEntry(frame_filtros, date_pattern='yyyy-mm-dd', width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_fim.grid(row=0, column=3, padx=5, pady=5)

        btn_gerar = ttk.Button(frame_filtros, text="Gerar Relatório", command=self.gerar_relatorios)
        btn_gerar.grid(row=0, column=4, padx=20, pady=5)

        # --- Notebook para abas de relatórios ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_geral = ttk.Frame(self.notebook)
        self.tab_pagamentos = ttk.Frame(self.notebook)
        self.tab_produtos = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_geral, text="Resumo Geral")
        self.notebook.add(self.tab_pagamentos, text="Formas de Pagamento")
        self.notebook.add(self.tab_produtos, text="Produtos Mais Vendidos")
        
        # Conteúdo inicial em branco
        self.gerar_relatorios()

    def limpar_abas(self):
        for tab in [self.tab_geral, self.tab_pagamentos, self.tab_produtos]:
            for widget in tab.winfo_children():
                widget.destroy()

    def gerar_relatorios(self):
        data_inicio = self.date_inicio.get_date().strftime('%Y-%m-%d')
        data_fim = self.date_fim.get_date().strftime('%Y-%m-%d')

        if data_inicio > data_fim:
            messagebox.showerror("Erro de Data", "A data de início não pode ser posterior à data de fim.")
            return

        self.limpar_abas()
        self.gerar_relatorio_geral(data_inicio, data_fim)
        self.gerar_relatorio_pagamentos(data_inicio, data_fim)
        self.gerar_relatorio_produtos(data_inicio, data_fim)

    def gerar_relatorio_geral(self, data_inicio, data_fim):
        dados = banco.get_relatorio_vendas(data_inicio, data_fim)
        
        num_vendas = dados[0] if dados and dados[0] is not None else 0
        total_faturado = dados[1] if dados and dados[1] is not None else 0.0
        ticket_medio = (total_faturado / num_vendas) if num_vendas > 0 else 0.0
        
        frame = ttk.Frame(self.tab_geral, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Resumo de Vendas do Período", font=("Arial", 16, "bold")).pack(pady=10)
        self.criar_card(frame, "Total Faturado", f"R$ {total_faturado:.2f}", "blue")
        self.criar_card(frame, "Número de Vendas", f"{num_vendas}", "green")
        self.criar_card(frame, "Ticket Médio", f"R$ {ticket_medio:.2f}", "purple")

    def criar_card(self, parent, titulo, valor, cor):
        card = tk.Frame(parent, bg=cor, bd=5, relief="raised")
        card.pack(pady=15, padx=20, fill="x")
        ttk.Label(card, text=titulo, font=("Arial", 14), background=cor, foreground="white").pack(pady=(10, 0))
        ttk.Label(card, text=valor, font=("Arial", 22, "bold"), background=cor, foreground="white").pack(pady=(5, 10))

    def gerar_relatorio_pagamentos(self, data_inicio, data_fim):
        dados = banco.get_vendas_por_forma_pagamento(data_inicio, data_fim)
        
        if not dados:
            ttk.Label(self.tab_pagamentos, text="Nenhum dado encontrado para o período.", font=("Arial", 12)).pack(pady=50)
            return

        labels = [item[0] for item in dados]
        sizes = [item[1] for item in dados]

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.4))
        ax.set_title("Distribuição por Forma de Pagamento", pad=20)
        ax.axis('equal') # Garante que a pizza seja um círculo.

        canvas = FigureCanvasTkAgg(fig, master=self.tab_pagamentos)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        plt.close(fig)

    def gerar_relatorio_produtos(self, data_inicio, data_fim):
        dados = banco.get_produtos_mais_vendidos(data_inicio, data_fim)

        frame_tabela = ttk.Frame(self.tab_produtos, padding=10)
        frame_tabela.pack(fill="both", expand=True)

        if not dados:
            ttk.Label(frame_tabela, text="Nenhum dado encontrado para o período.", font=("Arial", 12)).pack(pady=50)
            return

        tree = ttk.Treeview(frame_tabela, columns=("rank", "nome", "qtd", "valor"), show="headings")
        tree.heading("rank", text="Rank")
        tree.heading("nome", text="Produto")
        tree.heading("qtd", text="Qtd/Peso Vendido", anchor="center")
        tree.heading("valor", text="Valor Total (R$)", anchor="e")

        tree.column("rank", width=50, anchor="center")
        tree.column("nome", width=400)
        tree.column("qtd", width=150, anchor="center")
        tree.column("valor", width=150, anchor="e")

        for i, (nome, qtd, valor) in enumerate(dados, 1):
            tree.insert("", "end", values=(f"#{i}", nome, f"{qtd:.3f}", f"{valor:.2f}"))
        
        tree.pack(fill="both", expand=True)
