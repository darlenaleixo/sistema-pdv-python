# pdv_gestao.py
import tkinter as tk
from tkinter import ttk, messagebox
import banco
from estoque import JanelaEstoque
from pagamento import JanelaPagamento
from login import JanelaLogin
from operadores import JanelaOperadores
from relatorios import JanelaRelatorios
from configuracao import JanelaConfiguracao

class AppGestao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDV - Módulo de Gestão")
        self.withdraw()

        banco.criar_tabelas()
        self.iniciar_login()

    def iniciar_login(self):
        login = JanelaLogin(self)
        self.wait_window(login)

        if hasattr(login, 'operador_logado') and login.operador_logado:
            self.operador_logado = login.operador_logado
            # Verifica se o usuário é Administrador
            if self.operador_logado[2] != 'Admin':
                messagebox.showerror("Acesso Negado", "Apenas administradores podem aceder a este módulo.")
                self.destroy()
                return
            self.iniciar_app_principal()
        else:
            self.destroy()

    def iniciar_app_principal(self):
        self.deiconify()
        self.geometry("800x600")
        self.configure(bg="#d0d0d0")
        
        self.criar_menu_gestao()

        # Tela de boas-vindas
        ttk.Label(self, text="Módulo de Gestão", font=("Arial", 24, "bold")).pack(pady=50)
        ttk.Label(self, text="Utilize o menu superior para aceder às funcionalidades.", font=("Arial", 12)).pack()
        
        self.protocol("WM_DELETE_WINDOW", self.fechar_app)

    def criar_menu_gestao(self):
        """Cria o menu completo com todas as funções de gerenciamento."""
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Menu Gerenciar
        menu_gerenciar = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Gerenciar", menu=menu_gerenciar)
        menu_gerenciar.add_command(label="Estoque de Produtos", command=self.abrir_janela_estoque)
        menu_gerenciar.add_command(label="Formas de Pagamento", command=self.abrir_janela_pagamento)
        menu_gerenciar.add_separator()
        menu_gerenciar.add_command(label="Operadores", command=self.abrir_janela_operadores)
        menu_gerenciar.add_command(label="Relatórios", command=self.abrir_janela_relatorios)
        menu_gerenciar.add_separator()
        menu_gerenciar.add_command(label="Configurações", command=self.abrir_janela_configuracao)

        # Menu Usuário
        menu_usuario = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=f"Admin: {self.operador_logado[1]}", menu=menu_usuario)
        menu_usuario.add_command(label="Sair do Sistema", command=self.fechar_app)

    def fechar_app(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do módulo de gestão?"):
            self.destroy()

    # Funções para abrir as janelas
    def abrir_janela_estoque(self): JanelaEstoque(self)
    def abrir_janela_pagamento(self): JanelaPagamento(self)
    def abrir_janela_operadores(self): JanelaOperadores(self)
    def abrir_janela_relatorios(self): JanelaRelatorios(self)
    def abrir_janela_configuracao(self): JanelaConfiguracao(self)

if __name__ == "__main__":
    app = AppGestao()
    app.mainloop()
