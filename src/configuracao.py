# configuracao.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from escpos.printer import Usb # pip install python-escpos

CONFIG_FILE = 'config.json'

def carregar_configuracoes():
    """Carrega as configurações do arquivo JSON. Se não existir, cria um padrão."""
    defaults = {
        "loja_nome": "Nome da Sua Loja",
        "loja_endereco": "Seu Endereço, 123",
        "loja_telefone_cnpj": "CNPJ: 00.000.000/0001-00",
        "impressora_vendor_id": "",
        "impressora_product_id": "",
        "balanca_usa": False,
        "balanca_prefixo": "2",
        "balanca_tam_codigo": "5",
        "balanca_tam_valor": "5",
        "balanca_tipo_valor": "preco" # 'preco' ou 'peso'
    }
    if not os.path.exists(CONFIG_FILE):
        return defaults
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_lida = json.load(f)
            # Garante que todas as chaves padrão existam
            defaults.update(config_lida)
            return defaults
    except (json.JSONDecodeError, FileNotFoundError):
        return defaults

def salvar_configuracoes(config):
    """Salva o dicionário de configurações no arquivo JSON."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

class JanelaConfiguracao(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurações do Sistema")
        self.geometry("650x550")
        self.configure(bg="#f0f0f0")
        self.transient(parent)
        self.grab_set()

        self.config = carregar_configuracoes()
        self.criar_widgets()

    def criar_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(padx=10, pady=10, fill="both", expand=True)

        tab_loja = ttk.Frame(notebook)
        tab_impressora = ttk.Frame(notebook)
        tab_balanca = ttk.Frame(notebook) # Nova aba
        notebook.add(tab_loja, text="Dados da Loja")
        notebook.add(tab_impressora, text="Impressora")
        notebook.add(tab_balanca, text="Etiqueta da Balança")

        self.criar_aba_loja(tab_loja)
        self.criar_aba_impressora(tab_impressora)
        self.criar_aba_balanca(tab_balanca) # Cria a nova aba

        btn_salvar = ttk.Button(self, text="Salvar Configurações", command=self.salvar)
        btn_salvar.pack(pady=10)

    def criar_aba_loja(self, parent):
        frame = ttk.LabelFrame(parent, text="Informações do Recibo", padding=15)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Nome da Loja:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_loja_nome = ttk.Entry(frame, width=50)
        self.entry_loja_nome.grid(row=0, column=1, pady=5)
        self.entry_loja_nome.insert(0, self.config.get("loja_nome", ""))

        ttk.Label(frame, text="Endereço:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_loja_endereco = ttk.Entry(frame, width=50)
        self.entry_loja_endereco.grid(row=1, column=1, pady=5)
        self.entry_loja_endereco.insert(0, self.config.get("loja_endereco", ""))

        ttk.Label(frame, text="Telefone/CNPJ:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_loja_tel_cnpj = ttk.Entry(frame, width=50)
        self.entry_loja_tel_cnpj.grid(row=2, column=1, pady=5)
        self.entry_loja_tel_cnpj.insert(0, self.config.get("loja_telefone_cnpj", ""))

    def criar_aba_impressora(self, parent):
        frame = ttk.LabelFrame(parent, text="Seleção de Impressora Térmica", padding=15)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        ttk.Label(frame, text="Impressoras USB Encontradas:").pack(pady=5)
        
        self.listbox_impressoras = tk.Listbox(frame, height=5)
        self.listbox_impressoras.pack(pady=5, fill="x", expand=True)
        
        btn_detectar = ttk.Button(frame, text="Detectar Impressoras", command=self.detectar_impressoras)
        btn_detectar.pack(pady=10)
        
        ttk.Label(frame, text="Selecione a impressora na lista e clique em 'Salvar'.").pack()
        
        self.detectar_impressoras()

    def criar_aba_balanca(self, parent):
        frame = ttk.LabelFrame(parent, text="Formato do Código de Barras da Balança", padding=15)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.balanca_usa_var = tk.BooleanVar(value=self.config.get("balanca_usa", False))
        chk_usa_balanca = ttk.Checkbutton(frame, text="Habilitar leitura de etiqueta de balança", variable=self.balanca_usa_var)
        chk_usa_balanca.pack(anchor="w", pady=10)

        ttk.Label(frame, text="Prefixo (dígito inicial da etiqueta):").pack(anchor="w")
        self.entry_balanca_prefixo = ttk.Entry(frame, width=10)
        self.entry_balanca_prefixo.pack(anchor="w", pady=2, padx=5)
        self.entry_balanca_prefixo.insert(0, self.config.get("balanca_prefixo", "2"))

        ttk.Label(frame, text="Tamanho do Código do Produto (nº de dígitos):").pack(anchor="w", pady=(10,0))
        self.entry_balanca_tam_codigo = ttk.Entry(frame, width=10)
        self.entry_balanca_tam_codigo.pack(anchor="w", pady=2, padx=5)
        self.entry_balanca_tam_codigo.insert(0, self.config.get("balanca_tam_codigo", "5"))

        ttk.Label(frame, text="Tipo de Valor na Etiqueta:").pack(anchor="w", pady=(10,0))
        self.balanca_tipo_valor_var = tk.StringVar(value=self.config.get("balanca_tipo_valor", "preco"))
        ttk.Radiobutton(frame, text="Preço Total (ex: R$ 15,50)", variable=self.balanca_tipo_valor_var, value="preco").pack(anchor="w", padx=5)
        ttk.Radiobutton(frame, text="Peso (ex: 1,550 kg)", variable=self.balanca_tipo_valor_var, value="peso").pack(anchor="w", padx=5)

        ttk.Label(frame, text="Tamanho do Valor (Preço ou Peso):").pack(anchor="w", pady=(10,0))
        self.entry_balanca_tam_valor = ttk.Entry(frame, width=10)
        self.entry_balanca_tam_valor.pack(anchor="w", pady=2, padx=5)
        self.entry_balanca_tam_valor.insert(0, self.config.get("balanca_tam_valor", "5"))

        ttk.Label(frame, text="Exemplo: Código 2 12345 01550 7 (Prefixo, Código, Valor, Dígito Verificador)", font=("Arial", 8)).pack(anchor="w", pady=10)

    def detectar_impressoras(self):
        self.listbox_impressoras.delete(0, tk.END)
        try:
            self.impressoras_encontradas = Usb.find_all()
            if not self.impressoras_encontradas:
                self.listbox_impressoras.insert(tk.END, "Nenhuma impressora USB encontrada.")
                return

            for p in self.impressoras_encontradas:
                try:
                    p.open()
                    nome_produto = p.product_name
                    p.close()
                except Exception:
                    nome_produto = "Dispositivo USB"

                display_text = f"{nome_produto} (ID: {hex(p.idVendor)}:{hex(p.idProduct)})"
                self.listbox_impressoras.insert(tk.END, display_text)
                
                if hex(p.idVendor) == self.config.get("impressora_vendor_id") and \
                   hex(p.idProduct) == self.config.get("impressora_product_id"):
                    self.listbox_impressoras.selection_set(tk.END)

        except Exception as e:
            messagebox.showerror("Erro de Impressora", f"Não foi possível detectar impressoras: {e}\nVerifique se os drivers estão instalados.")

    def salvar(self):
        self.config["loja_nome"] = self.entry_loja_nome.get()
        self.config["loja_endereco"] = self.entry_loja_endereco.get()
        self.config["loja_telefone_cnpj"] = self.entry_loja_tel_cnpj.get()

        selecionado = self.listbox_impressoras.curselection()
        if selecionado:
            impressora = self.impressoras_encontradas[selecionado[0]]
            self.config["impressora_vendor_id"] = hex(impressora.idVendor)
            self.config["impressora_product_id"] = hex(impressora.idProduct)
        
        # Salvar configurações da balança
        self.config["balanca_usa"] = self.balanca_usa_var.get()
        self.config["balanca_prefixo"] = self.entry_balanca_prefixo.get()
        self.config["balanca_tam_codigo"] = self.entry_balanca_tam_codigo.get()
        self.config["balanca_tipo_valor"] = self.balanca_tipo_valor_var.get()
        self.config["balanca_tam_valor"] = self.entry_balanca_tam_valor.get()

        try:
            salvar_configuracoes(self.config)
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar as configurações: {e}")
