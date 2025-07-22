# vendas.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import banco
from datetime import datetime
from impressao import imprimir_recibo
from configuracao import carregar_configuracoes

class JanelaVendas(tk.Frame):
    def __init__(self, parent, operador_logado):
        super().__init__(parent, bg="#e0e0e0")
        self.parent = parent
        self.operador_logado = operador_logado
        self.carrinho = []
        self.config = carregar_configuracoes() # Carrega as configs aqui
        
        self.criar_widgets()
        self.configurar_atalhos()

    def criar_widgets(self):
        # (O código para criar os widgets da janela de vendas permanece o mesmo)
        frame_esquerda = tk.Frame(self, bg="#e0e0e0", padx=10, pady=10)
        frame_esquerda.pack(side="left", fill="y")
        frame_operador = ttk.LabelFrame(frame_esquerda, text="Operador")
        frame_operador.pack(fill="x", pady=(0, 10))
        ttk.Label(frame_operador, text=f"{self.operador_logado[1]} ({self.operador_logado[2]})", font=("Arial", 10)).pack(padx=10, pady=5)
        frame_codigo = ttk.LabelFrame(frame_esquerda, text="Código do Produto (Qtd/Peso*Código)")
        frame_codigo.pack(fill="x", pady=10)
        self.entry_codigo = ttk.Entry(frame_codigo, font=("Arial", 18))
        self.entry_codigo.pack(padx=10, pady=10)
        self.entry_codigo.bind("<Return>", self.adicionar_produto_carrinho)
        self.entry_codigo.focus_set()
        frame_total = tk.Frame(frame_esquerda, bg="#333", bd=5, relief="sunken")
        frame_total.pack(fill="x", pady=20)
        ttk.Label(frame_total, text="TOTAL (R$)", font=("Arial", 16, "bold"), foreground="white", background="#333").pack()
        self.label_total = ttk.Label(frame_total, text="0.00", font=("Arial", 36, "bold"), foreground="#00ff00", background="#333")
        self.label_total.pack(pady=10)
        frame_botoes = tk.Frame(frame_esquerda, bg="#e0e0e0")
        frame_botoes.pack(fill="x", pady=10)
        self.btn_finalizar = ttk.Button(frame_botoes, text="F12 - Finalizar Venda", command=self.abrir_finalizar_venda)
        self.btn_finalizar.pack(fill="x", pady=5)
        self.btn_cancelar_item = ttk.Button(frame_botoes, text="F5 - Cancelar Último Item", command=self.cancelar_ultimo_item)
        self.btn_cancelar_item.pack(fill="x", pady=5)
        self.btn_limpar_venda = ttk.Button(frame_botoes, text="F6 - Limpar Venda", command=self.limpar_venda)
        self.btn_limpar_venda.pack(fill="x", pady=5)
        frame_direita = ttk.LabelFrame(self, text="Itens da Venda", padding=10)
        frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        colunas = ("nome", "qtd", "preco_unit", "subtotal")
        self.tree_venda = ttk.Treeview(frame_direita, columns=colunas, show="headings")
        self.tree_venda.heading("nome", text="Nome")
        self.tree_venda.heading("qtd", text="Qtd/Peso", anchor="center")
        self.tree_venda.heading("preco_unit", text="Vlr. Unit/kg", anchor="e")
        self.tree_venda.heading("subtotal", text="Subtotal", anchor="e")
        self.tree_venda.column("nome", width=300)
        self.tree_venda.column("qtd", width=80, anchor="center")
        self.tree_venda.column("preco_unit", width=100, anchor="e")
        self.tree_venda.column("subtotal", width=100, anchor="e")
        scrollbar = ttk.Scrollbar(frame_direita, orient="vertical", command=self.tree_venda.yview)
        self.tree_venda.configure(yscrollcommand=scrollbar.set)
        self.tree_venda.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def configurar_atalhos(self):
        self.parent.bind("<F12>", lambda event: self.abrir_finalizar_venda())
        self.parent.bind("<F5>", lambda event: self.cancelar_ultimo_item())
        self.parent.bind("<F6>", lambda event: self.limpar_venda())

    def adicionar_produto_carrinho(self, event=None):
        codigo_input = self.entry_codigo.get().strip().replace(',', '.')
        if not codigo_input: return

        # Tenta interpretar como etiqueta de balança primeiro
        if self.config.get("balanca_usa") and codigo_input.startswith(self.config.get("balanca_prefixo")):
            if self.processar_etiqueta_balanca(codigo_input):
                self.entry_codigo.delete(0, tk.END)
                self.atualizar_tela_venda()
                return # Sai da função se processou com sucesso

        # Se não for etiqueta de balança, continua com o fluxo normal
        quantidade = 1.0
        codigo_produto = codigo_input

        if '*' in codigo_input:
            try:
                partes = codigo_input.split('*')
                if len(partes) == 2:
                    quantidade = float(partes[0])
                    codigo_produto = partes[1]
                else: raise ValueError
            except (ValueError, IndexError):
                messagebox.showerror("Entrada Inválida", "Formato inválido. Use 'Qtd*Código' ou 'Peso*Código'.")
                self.entry_codigo.delete(0, tk.END)
                return

        self.adicionar_item(codigo_produto, quantidade)
        self.entry_codigo.delete(0, tk.END)
        self.atualizar_tela_venda()

    def processar_etiqueta_balanca(self, codigo_barras):
        try:
            prefixo = self.config["balanca_prefixo"]
            tam_codigo = int(self.config["balanca_tam_codigo"])
            tam_valor = int(self.config["balanca_tam_valor"])
            tipo_valor = self.config["balanca_tipo_valor"]

            # Posições dos dados no código de barras
            inicio_codigo = len(prefixo)
            fim_codigo = inicio_codigo + tam_codigo
            inicio_valor = fim_codigo
            fim_valor = inicio_valor + tam_valor

            # Extrai os dados
            codigo_produto = codigo_barras[inicio_codigo:fim_codigo]
            valor_str = codigo_barras[inicio_valor:fim_valor]
            
            produto = banco.buscar_produto_por_codigo(codigo_produto)
            if not produto:
                messagebox.showerror("Erro", f"Produto com código '{codigo_produto}' da etiqueta não encontrado.")
                return False

            if tipo_valor == 'preco':
                preco_total = float(valor_str) / 100
                quantidade = preco_total / produto[2] # produto[2] é o preço/kg
            elif tipo_valor == 'peso':
                quantidade = float(valor_str) / 1000 # Assume que o peso está em gramas
            else:
                return False

            return self.adicionar_item(codigo_produto, quantidade)

        except (ValueError, IndexError, TypeError):
            messagebox.showerror("Erro de Etiqueta", "Não foi possível ler a etiqueta da balança. Verifique as configurações.")
            return False

    def adicionar_item(self, codigo_produto, quantidade):
        produto = banco.buscar_produto_por_codigo(codigo_produto)
        if not produto:
            messagebox.showerror("Erro", f"Produto com código '{codigo_produto}' não encontrado.")
            return False

        codigo, nome, preco, estoque_atual, _, unidade = produto
        
        if unidade == 'un':
            quantidade = int(quantidade)
        
        if estoque_atual < quantidade:
            messagebox.showwarning("Stock Insuficiente", f"Produto '{nome}' com apenas {estoque_atual} {unidade} em stock.")
            return False
        
        self.carrinho.append([codigo, nome, quantidade, preco, preco * quantidade, unidade])
        return True

    def atualizar_tela_venda(self):
        # (O código desta função permanece o mesmo)
        for i in self.tree_venda.get_children(): self.tree_venda.delete(i)
        total_venda = 0
        for item in self.carrinho:
            codigo, nome, qtd, preco_unit, _, unidade = item
            subtotal = qtd * preco_unit
            item[4] = subtotal
            preco_unit_fmt = f"{preco_unit:.2f}"
            subtotal_fmt = f"{subtotal:.2f}"
            qtd_formatada = f"{int(qtd)}" if unidade == 'un' else f"{qtd:.3f}"
            self.tree_venda.insert("", "end", values=(nome, f"{qtd_formatada} {unidade}", preco_unit_fmt, subtotal_fmt))
            total_venda += subtotal
        self.label_total.config(text=f"{total_venda:.2f}")

    def cancelar_ultimo_item(self):
        # (O código desta função permanece o mesmo)
        if self.carrinho:
            item_removido = self.carrinho.pop()
            messagebox.showinfo("Item Removido", f"Item '{item_removido[1]}' removido da venda.")
            self.atualizar_tela_venda()
        else:
            messagebox.showwarning("Carrinho Vazio", "Não há itens para remover.")

    def limpar_venda(self):
        # (O código desta função permanece o mesmo)
        if self.carrinho and messagebox.askyesno("Limpar Venda", "Tem certeza que deseja limpar todos os itens da venda atual?"):
            self.carrinho.clear()
            self.atualizar_tela_venda()
            self.entry_codigo.focus_set()

    def abrir_finalizar_venda(self):
        # (O código desta função permanece o mesmo)
        if not self.carrinho:
            messagebox.showwarning("Venda Vazia", "Adicione produtos antes de finalizar a venda.")
            return
        total = float(self.label_total.cget("text"))
        JanelaFinalizarVenda(self, total, self.carrinho, self.operador_logado)

class JanelaFinalizarVenda(tk.Toplevel):
    # (A classe JanelaFinalizarVenda permanece a mesma da etapa anterior)
    def __init__(self, parent_venda, total, carrinho, operador_logado):
        super().__init__(parent_venda.parent)
        self.parent_venda = parent_venda
        self.total = total
        self.carrinho = carrinho
        self.operador_logado = operador_logado
        self.title("Finalizar Venda")
        self.geometry("400x400")
        self.configure(bg="#f0f0f0")
        self.transient(parent_venda.parent)
        self.grab_set()
        self.criar_widgets()

    def criar_widgets(self):
        ttk.Label(self, text="Total da Venda:", font=("Arial", 14)).pack(pady=(10,0))
        ttk.Label(self, text=f"R$ {self.total:.2f}", font=("Arial", 24, "bold"), foreground="blue").pack()
        ttk.Label(self, text="Forma de Pagamento:", font=("Arial", 12)).pack(pady=(20, 5))
        self.combo_pagamento = ttk.Combobox(self, values=banco.listar_formas_pagamento(), font=("Arial", 12), state="readonly")
        self.combo_pagamento.pack()
        self.combo_pagamento.set("Dinheiro")
        self.combo_pagamento.bind("<<ComboboxSelected>>", self.verificar_pagamento_dinheiro)
        self.frame_troco = ttk.Frame(self, bg="#f0f0f0")
        self.frame_troco.pack(pady=10)
        ttk.Label(self.frame_troco, text="Valor Recebido (R$):", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.entry_valor_recebido = ttk.Entry(self.frame_troco, font=("Arial", 12))
        self.entry_valor_recebido.grid(row=0, column=1, padx=5)
        self.entry_valor_recebido.bind("<KeyRelease>", self.calcular_troco)
        ttk.Label(self.frame_troco, text="Troco (R$):", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.label_troco = ttk.Label(self.frame_troco, text="0.00", font=("Arial", 14, "bold"), foreground="green")
        self.label_troco.grid(row=1, column=1, padx=5, pady=5)
        self.imprimir_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Imprimir Recibo", variable=self.imprimir_var).pack(pady=10)
        ttk.Button(self, text="Confirmar Venda", command=self.confirmar_venda).pack(pady=10, ipadx=10, ipady=5)
    
    def verificar_pagamento_dinheiro(self, event=None):
        if self.combo_pagamento.get() != "Dinheiro":
            self.entry_valor_recebido.delete(0, tk.END)
            self.entry_valor_recebido.config(state="disabled")
            self.label_troco.config(text="0.00")
        else:
            self.entry_valor_recebido.config(state="normal")

    def calcular_troco(self, event=None):
        try:
            valor_recebido_str = self.entry_valor_recebido.get().replace(',', '.')
            if not valor_recebido_str:
                self.label_troco.config(text="0.00")
                return
            valor_recebido = float(valor_recebido_str)
            troco = valor_recebido - self.total
            if troco < 0:
                self.label_troco.config(text="Valor insuficiente", foreground="red")
            else:
                self.label_troco.config(text=f"{troco:.2f}", foreground="green")
        except ValueError:
            self.label_troco.config(text="Inválido", foreground="red")

    def confirmar_venda(self):
        forma_pagamento = self.combo_pagamento.get()
        if not forma_pagamento:
            messagebox.showwarning("Aviso", "Selecione uma forma de pagamento.")
            return
        troco = 0.0
        if forma_pagamento == "Dinheiro":
            try:
                valor_recebido_str = self.entry_valor_recebido.get().replace(',', '.')
                if not valor_recebido_str:
                    messagebox.showerror("Erro", "Valor recebido em dinheiro deve ser informado.")
                    return
                valor_recebido = float(valor_recebido_str)
                if valor_recebido < self.total:
                    messagebox.showerror("Erro", "Valor recebido é menor que o total da venda.")
                    return
                troco = valor_recebido - self.total
            except (ValueError, TypeError):
                 messagebox.showerror("Erro", "Valor recebido em dinheiro é inválido.")
                 return
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        operador_id = self.operador_logado[0]
        venda_id = banco.registrar_venda(operador_id, data_hora, self.total, forma_pagamento, self.carrinho)
        if venda_id:
            if self.imprimir_var.get():
                imprimir_recibo(venda_id, self.total, forma_pagamento, troco, self.carrinho, self.operador_logado[1])
            self.parent_venda.carrinho.clear()
            self.parent_venda.atualizar_tela_venda()
            self.parent_venda.entry_codigo.focus_set()
            self.destroy()
