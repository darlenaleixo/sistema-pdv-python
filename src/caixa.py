# caixa.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import banco

class JanelaAberturaCaixa(tk.Toplevel):
    def __init__(self, parent, operador_id):
        super().__init__(parent)
        self.parent = parent
        self.operador_id = operador_id
        self.caixa_id = None

        self.title("Abertura de Caixa")
        self.geometry("350x200")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancelar_abertura)

        self.criar_widgets()

    def criar_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True)

        ttk.Label(frame, text="Valor Inicial (Fundo de Troco): R$").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_valor = ttk.Entry(frame, width=20, font=("Arial", 12))
        self.entry_valor.grid(row=1, column=0, pady=5)
        self.entry_valor.focus_set()
        self.entry_valor.bind("<Return>", self.confirmar_abertura)

        btn_confirmar = ttk.Button(frame, text="Abrir Caixa", command=self.confirmar_abertura)
        btn_confirmar.grid(row=2, column=0, pady=20)

    def confirmar_abertura(self, event=None):
        valor_str = self.entry_valor.get().strip().replace(',', '.')
        try:
            valor_inicial = float(valor_str)
            if valor_inicial < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valor Inválido", "Por favor, insira um valor monetário válido.")
            return
        
        self.caixa_id = banco.abrir_caixa(self.operador_id, valor_inicial)
        if self.caixa_id:
            self.destroy()

    def cancelar_abertura(self):
        if messagebox.askokcancel("Cancelar", "Nenhum caixa foi aberto. Deseja sair do sistema?"):
            self.parent.destroy()

class JanelaFechamentoCaixa(tk.Toplevel):
    def __init__(self, parent, caixa_aberto, operador_logado):
        super().__init__(parent)
        self.parent = parent
        self.caixa_id = caixa_aberto[0]
        self.valor_inicial = caixa_aberto[3]
        self.data_abertura = caixa_aberto[2]
        self.operador_logado = operador_logado

        self.title("Fechamento de Caixa")
        self.geometry("450x450")
        self.configure(bg="#f0f0f0")
        self.transient(parent)
        self.grab_set()

        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # --- Seção de Resumo ---
        frame_resumo = ttk.LabelFrame(main_frame, text="Resumo do Caixa", padding=10)
        frame_resumo.pack(fill="x")

        self.add_resumo_row(frame_resumo, "Valor de Abertura (Troco):", f"R$ {self.valor_inicial:.2f}", 0)
        self.lbl_vendas_dinheiro = self.add_resumo_row(frame_resumo, "Vendas em Dinheiro:", "R$ 0.00", 1)
        self.lbl_sangrias = self.add_resumo_row(frame_resumo, "Total de Sangrias:", "R$ 0.00", 2)
        self.lbl_valor_calculado = self.add_resumo_row(frame_resumo, "Valor Esperado no Caixa:", "R$ 0.00", 3, bold=True)
        
        # --- Seção de Fechamento ---
        frame_fechamento = ttk.LabelFrame(main_frame, text="Contagem Final", padding=10)
        frame_fechamento.pack(fill="x", pady=15)

        ttk.Label(frame_fechamento, text="Valor Contado no Caixa (R$):").pack(pady=5)
        self.entry_valor_contado = ttk.Entry(frame_fechamento, font=("Arial", 14), justify="center")
        self.entry_valor_contado.pack(pady=5)
        self.entry_valor_contado.bind("<KeyRelease>", self.calcular_diferenca)

        ttk.Label(frame_fechamento, text="Diferença (Quebra de Caixa):").pack(pady=10)
        self.lbl_diferenca = ttk.Label(frame_fechamento, text="R$ 0.00", font=("Arial", 16, "bold"))
        self.lbl_diferenca.pack()

        # --- Botão ---
        btn_fechar = ttk.Button(main_frame, text="Confirmar e Fechar Caixa", command=self.confirmar_fechamento)
        btn_fechar.pack(pady=20)

    def add_resumo_row(self, parent, label_text, value_text, row, bold=False):
        font_style = ("Arial", 10, "bold") if bold else ("Arial", 10)
        ttk.Label(parent, text=label_text, font=font_style).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        lbl_value = ttk.Label(parent, text=value_text, font=font_style)
        lbl_value.grid(row=row, column=1, sticky="e", padx=5, pady=2)
        return lbl_value

    def carregar_dados(self):
        vendas_dinheiro, sangrias = banco.get_dados_fechamento(self.caixa_id, self.data_abertura)
        
        self.valor_calculado = self.valor_inicial + vendas_dinheiro - sangrias
        
        self.lbl_vendas_dinheiro.config(text=f"R$ {vendas_dinheiro:.2f}")
        self.lbl_sangrias.config(text=f"R$ {sangrias:.2f}")
        self.lbl_valor_calculado.config(text=f"R$ {self.valor_calculado:.2f}")
        
        self.calcular_diferenca()

    def calcular_diferenca(self, event=None):
        try:
            valor_contado_str = self.entry_valor_contado.get().strip().replace(',', '.')
            if not valor_contado_str:
                valor_contado = 0.0
            else:
                valor_contado = float(valor_contado_str)
        except ValueError:
            self.lbl_diferenca.config(text="Valor inválido", foreground="orange")
            return

        diferenca = valor_contado - self.valor_calculado
        
        cor = "green"
        if diferenca < 0:
            cor = "red" # Faltou
        elif diferenca > 0:
            cor = "blue" # Sobrou
            
        self.lbl_diferenca.config(text=f"R$ {diferenca:.2f}", foreground=cor)

    def confirmar_fechamento(self):
        try:
            valor_contado = float(self.entry_valor_contado.get().strip().replace(',', '.'))
        except ValueError:
            messagebox.showerror("Erro", "O valor contado é inválido.")
            return

        diferenca = valor_contado - self.valor_calculado

        msg = f"Deseja fechar o caixa?\n\nValor Esperado: R$ {self.valor_calculado:.2f}\nValor Contado: R$ {valor_contado:.2f}\nDiferença: R$ {diferenca:.2f}"
        if messagebox.askyesno("Confirmar Fechamento", msg):
            sucesso = banco.fechar_caixa(self.caixa_id, self.valor_calculado, valor_contado, diferenca)
            if sucesso:
                messagebox.showinfo("Sucesso", "Caixa fechado com sucesso! O sistema será encerrado.")
                self.parent.destroy()
