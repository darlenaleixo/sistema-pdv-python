# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import banco
from vendas import JanelaVendas
from estoque import JanelaEstoque
from pagamento import JanelaPagamento
from login import JanelaLogin
from operadores import JanelaOperadores
from caixa import JanelaAberturaCaixa, JanelaFechamentoCaixa
from relatorios import JanelaRelatorios
from configuracao import JanelaConfiguracao

class AppPDV(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Vendas PDV")
        self.withdraw()

        banco.criar_tabelas()
        self.iniciar_login()

    def iniciar_login(self):
        login = JanelaLogin(self)
        self.wait_window(login)

        if hasattr(login, 'operador_logado') and login.operador_logado:
            self.operador_logado = login.operador_logado
            self.verificar_caixa()
        else:
            self.destroy()

    def verificar_caixa(self):
        self.caixa_aberto = banco.get_caixa_aberto(self.operador_logado[0])
        if self.caixa_aberto:
            self.iniciar_app_principal()
        else:
            abertura = JanelaAberturaCaixa(self, self.operador_logado[0])
            self.wait_window(abertura)
            if hasattr(abertura, 'caixa_id') and abertura.caixa_id:
                self.caixa_aberto = banco.get_caixa_aberto(self.operador_logado[0])
                self.iniciar_app_principal()
            else:
                self.iniciar_login()

    def iniciar_app_principal(self):
        self.deiconify()
        self.state('zoomed') 
        self.configure(bg="#333")
        
        self.criar_menu()
        
        self.janela_vendas = JanelaVendas(self, self.operador_logado)
        self.janela_vendas.pack(fill="both", expand=True)
        
        self.protocol("WM_DELETE_WINDOW", self.fechar_app)

    def criar_menu(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Menu Gerenciar
        menu_gerenciar = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Gerenciar", menu=menu_gerenciar)
        menu_gerenciar.add_command(label="Estoque de Produtos", command=self.abrir_janela_estoque)
        menu_gerenciar.add_command(label="Formas de Pagamento", command=self.abrir_janela_pagamento)
        
        if self.operador_logado[2] == 'Admin':
            menu_gerenciar.add_separator()
            menu_gerenciar.add_command(label="Operadores", command=self.abrir_janela_operadores)
            menu_gerenciar.add_command(label="Relatórios", command=self.abrir_janela_relatorios)
            menu_gerenciar.add_separator()
            menu_gerenciar.add_command(label="Configurações", command=self.abrir_janela_configuracao)

        # Menu Caixa
        menu_caixa = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Caixa", menu=menu_caixa)
        menu_caixa.add_command(label="Registar Sangria", command=self.registar_sangria)
        menu_caixa.add_separator()
        menu_caixa.add_command(label="Fechar Caixa", command=self.fechar_caixa)

        # Menu Usuário
        menu_usuario = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=f"Usuário: {self.operador_logado[1]}", menu=menu_usuario)
        menu_usuario.add_command(label="Trocar de Usuário (Logout)", command=self.fazer_logout)
        menu_usuario.add_command(label="Sair do Sistema", command=self.fechar_app)

    def registar_sangria(self):
        valor = simpledialog.askfloat("Registar Sangria", "Digite o valor a ser retirado do caixa:", parent=self)
        if valor is not None and valor > 0:
            caixa_id = self.caixa_aberto[0]
            operador_id = self.operador_logado[0]
            banco.registrar_sangria(caixa_id, operador_id, valor)
        elif valor is not None:
            messagebox.showwarning("Valor Inválido", "O valor da sangria deve ser positivo.")

    def fechar_caixa(self):
        JanelaFechamentoCaixa(self, self.caixa_aberto, self.operador_logado)

    def fazer_logout(self):
        if messagebox.askokcancel("Logout", "Isto irá fechar o caixa atual. Deseja continuar?"):
            self.fechar_caixa()

    def fechar_app(self):
        if messagebox.askokcancel("Sair", "Isto irá fechar o caixa atual. Deseja sair do sistema?"):
            self.fechar_caixa()

    def abrir_janela_estoque(self): JanelaEstoque(self)
    def abrir_janela_pagamento(self): JanelaPagamento(self)
    def abrir_janela_operadores(self): JanelaOperadores(self)
    def abrir_janela_relatorios(self): JanelaRelatorios(self)
    def abrir_janela_configuracao(self): JanelaConfiguracao(self)
    def mostrar_sobre(self):
        messagebox.showinfo("Sobre o Sistema PDV", 
                            "Sistema de Ponto de Venda v2.0 (Final)\n\n"
                            "Funcionalidades: Leitura de etiquetas de balança e todas as anteriores.")
