# login.py
import tkinter as tk
from tkinter import ttk, messagebox
import banco

class JanelaLogin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Login - Sistema PDV")
        self.geometry("350x200")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        
        # Centralizar a janela
        self.transient(parent)
        self.grab_set()
        
        self.operador_logado = None
        self.protocol("WM_DELETE_WINDOW", self.fechar_login)

        self.criar_widgets()

    def criar_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True)

        ttk.Label(frame, text="Nome de Usuário:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_usuario = ttk.Entry(frame, width=30)
        self.entry_usuario.grid(row=1, column=0, pady=5)
        self.entry_usuario.focus_set()

        ttk.Label(frame, text="Senha:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_senha = ttk.Entry(frame, width=30, show="*")
        self.entry_senha.grid(row=3, column=0, pady=5)
        self.entry_senha.bind("<Return>", self.fazer_login)

        self.label_erro = ttk.Label(frame, text="", foreground="red")
        self.label_erro.grid(row=4, column=0, pady=5)

        btn_login = ttk.Button(frame, text="Login", command=self.fazer_login)
        btn_login.grid(row=5, column=0, pady=10)

    def fazer_login(self, event=None):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            self.label_erro.config(text="Preencha todos os campos.")
            return

        operador = banco.verificar_login(usuario, senha)

        if operador:
            self.operador_logado = operador
            self.destroy() # Fecha a janela de login
        else:
            self.label_erro.config(text="Usuário ou senha inválidos.")
            self.entry_senha.delete(0, tk.END)

    def fechar_login(self):
        """ Se o usuário fechar a janela de login, o app principal fecha """
        self.parent.destroy()
