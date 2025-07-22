# banco.py
import sqlite3
import os
from tkinter import messagebox
import hashlib
from datetime import datetime

# (Funções conectar e criar_tabelas permanecem as mesmas)
def conectar():
    db_file = 'pdv_database.db'
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Não foi possível conectar ao banco de dados: {e}")
        return None

def criar_tabelas():
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS operadores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, nivel_acesso TEXT NOT NULL DEFAULT 'Operador')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (codigo TEXT PRIMARY KEY, nome TEXT NOT NULL, preco REAL NOT NULL, quantidade REAL NOT NULL, categoria TEXT, unidade TEXT NOT NULL DEFAULT 'un')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, operador_id INTEGER, data_hora TEXT NOT NULL, total REAL NOT NULL, forma_pagamento TEXT NOT NULL, FOREIGN KEY (operador_id) REFERENCES operadores (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_venda (id INTEGER PRIMARY KEY AUTOINCREMENT, venda_id INTEGER, produto_codigo TEXT, quantidade REAL, preco_unitario REAL, FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE, FOREIGN KEY (produto_codigo) REFERENCES produtos (codigo))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS formas_pagamento (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS caixa (id INTEGER PRIMARY KEY AUTOINCREMENT, operador_id INTEGER NOT NULL, data_abertura TEXT NOT NULL, valor_inicial REAL NOT NULL, data_fechamento TEXT, valor_final_calculado REAL, valor_final_contado REAL, diferenca REAL, status TEXT NOT NULL, FOREIGN KEY (operador_id) REFERENCES operadores (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sangrias (id INTEGER PRIMARY KEY AUTOINCREMENT, caixa_id INTEGER NOT NULL, operador_id INTEGER NOT NULL, data_hora TEXT NOT NULL, valor REAL NOT NULL, FOREIGN KEY (caixa_id) REFERENCES caixa (id), FOREIGN KEY (operador_id) REFERENCES operadores (id))''')
    cursor.execute("SELECT COUNT(*) FROM formas_pagamento")
    if cursor.fetchone()[0] == 0:
        pagamentos_padrao = [('Dinheiro',), ('Cartão de Crédito',), ('Cartão de Débito',), ('Pix',)]
        cursor.executemany("INSERT INTO formas_pagamento (nome) VALUES (?)", pagamentos_padrao)
    cursor.execute("SELECT COUNT(*) FROM operadores")
    if cursor.fetchone()[0] == 0:
        senha_hash = hashlib.sha256('admin'.encode()).hexdigest()
        cursor.execute("INSERT INTO operadores (nome, senha, nivel_acesso) VALUES (?, ?, ?)", ('admin', senha_hash, 'Admin'))
    conn.commit()
    conn.close()


def registrar_venda(operador_id, data_hora, total, forma_pagamento, itens):
    """Registra a venda e retorna o ID da venda em caso de sucesso."""
    conn = conectar()
    if conn is None: return None
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vendas (operador_id, data_hora, total, forma_pagamento) VALUES (?, ?, ?, ?)",
                       (operador_id, data_hora, total, forma_pagamento))
        venda_id = cursor.lastrowid # Captura o ID da venda inserida

        for item in itens:
            produto_codigo, _, quantidade_vendida, preco_unitario, _, _ = item
            cursor.execute("INSERT INTO itens_venda (venda_id, produto_codigo, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                           (venda_id, produto_codigo, quantidade_vendida, preco_unitario))
            cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE codigo = ?",
                           (quantidade_vendida, produto_codigo))
        conn.commit()
        messagebox.showinfo("Venda Finalizada", "Venda registada com sucesso!")
        return venda_id # Retorna o ID
    except sqlite3.Error as e:
        conn.rollback()
        messagebox.showerror("Erro de Venda", f"Não foi possível registar a venda: {e}")
        return None # Retorna None em caso de erro
    finally:
        conn.close()

# (O restante das funções do banco.py permanecem as mesmas)
def get_relatorio_vendas(data_inicio, data_fim):
    conn = conectar()
    if conn is None: return None
    cursor = conn.cursor()
    data_fim_completa = f"{data_fim} 23:59:59"
    cursor.execute('''SELECT COUNT(id), SUM(total) FROM vendas WHERE data_hora BETWEEN ? AND ?''', (data_inicio, data_fim_completa))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def get_vendas_por_forma_pagamento(data_inicio, data_fim):
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    data_fim_completa = f"{data_fim} 23:59:59"
    cursor.execute('''SELECT forma_pagamento, SUM(total) FROM vendas WHERE data_hora BETWEEN ? AND ? GROUP BY forma_pagamento ORDER BY SUM(total) DESC''', (data_inicio, data_fim_completa))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def get_produtos_mais_vendidos(data_inicio, data_fim):
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    data_fim_completa = f"{data_fim} 23:59:59"
    cursor.execute('''SELECT p.nome, SUM(iv.quantidade) as total_qtd, SUM(iv.quantidade * iv.preco_unitario) as total_valor FROM itens_venda iv JOIN produtos p ON iv.produto_codigo = p.codigo JOIN vendas v ON iv.venda_id = v.id WHERE v.data_hora BETWEEN ? AND ? GROUP BY p.nome ORDER BY total_valor DESC LIMIT 10''', (data_inicio, data_fim_completa))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def get_caixa_aberto(operador_id):
    conn = conectar()
    if conn is None: return None
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caixa WHERE operador_id = ? AND status = 'Aberto'", (operador_id,))
    caixa = cursor.fetchone()
    conn.close()
    return caixa

def abrir_caixa(operador_id, valor_inicial):
    conn = conectar()
    if conn is None: return None
    cursor = conn.cursor()
    try:
        data_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO caixa (operador_id, data_abertura, valor_inicial, status) VALUES (?, ?, ?, 'Aberto')", (operador_id, data_abertura, valor_inicial))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o caixa: {e}")
        return None
    finally:
        conn.close()

def fechar_caixa(caixa_id, valor_calculado, valor_contado, diferenca):
    conn = conectar()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        data_fechamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''UPDATE caixa SET data_fechamento = ?, valor_final_calculado = ?, valor_final_contado = ?, diferenca = ?, status = 'Fechado' WHERE id = ?''', (data_fechamento, valor_calculado, valor_contado, diferenca, caixa_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Não foi possível fechar o caixa: {e}")
        return False
    finally:
        conn.close()

def registrar_sangria(caixa_id, operador_id, valor):
    conn = conectar()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO sangrias (caixa_id, operador_id, data_hora, valor) VALUES (?, ?, ?, ?)", (caixa_id, operador_id, data_hora, valor))
        conn.commit()
        messagebox.showinfo("Sucesso", "Sangria registada com sucesso!")
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Não foi possível registar a sangria: {e}")
        return False
    finally:
        conn.close()

def get_dados_fechamento(caixa_id, data_abertura):
    conn = conectar()
    if conn is None: return (0, 0)
    cursor = conn.cursor()
    cursor.execute('''SELECT SUM(total) FROM vendas WHERE data_hora >= ? AND forma_pagamento = 'Dinheiro' ''', (data_abertura,))
    total_vendas_dinheiro = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(valor) FROM sangrias WHERE caixa_id = ?", (caixa_id,))
    total_sangrias = cursor.fetchone()[0] or 0.0
    conn.close()
    return total_vendas_dinheiro, total_sangrias

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_login(nome, senha):
    conn = conectar()
    if conn is None: return None
    cursor = conn.cursor()
    senha_hash = hash_senha(senha)
    cursor.execute("SELECT id, nome, nivel_acesso FROM operadores WHERE nome = ? AND senha = ?", (nome, senha_hash))
    operador = cursor.fetchone()
    conn.close()
    return operador

def adicionar_operador(nome, senha, nivel_acesso):
    conn = conectar()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        senha_hash = hash_senha(senha)
        cursor.execute("INSERT INTO operadores (nome, senha, nivel_acesso) VALUES (?, ?, ?)", (nome, senha_hash, nivel_acesso))
        conn.commit()
        messagebox.showinfo("Sucesso", "Operador registado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"O operador com nome '{nome}' já existe.")
        return False
    finally:
        conn.close()

def listar_operadores():
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, nivel_acesso FROM operadores")
    operadores = cursor.fetchall()
    conn.close()
    return operadores

def adicionar_produto(codigo, nome, preco, quantidade, categoria, unidade):
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO produtos (codigo, nome, preco, quantidade, categoria, unidade) VALUES (?, ?, ?, ?, ?, ?)", (codigo, nome, preco, quantidade, categoria, unidade))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"Produto com código '{codigo}' já existe.")
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
    finally:
        conn.close()

def buscar_produto_por_codigo(codigo):
    conn = conectar()
    if conn is None: return None
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))
    produto = cursor.fetchone()
    conn.close()
    return produto

def listar_produtos():
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def editar_produto(codigo, nome, preco, quantidade, categoria, unidade):
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE produtos SET nome = ?, preco = ?, quantidade = ?, categoria = ?, unidade = ? WHERE codigo = ?''', (nome, preco, quantidade, categoria, unidade, codigo))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
    finally:
        conn.close()

def excluir_produto(codigo):
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM produtos WHERE codigo = ?", (codigo,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
    finally:
        conn.close()

def buscar_produtos_estoque_baixo(limite=5):
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE quantidade <= ? AND unidade = 'un' ORDER BY quantidade", (limite,))
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def listar_formas_pagamento():
    conn = conectar()
    if conn is None: return []
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM formas_pagamento ORDER BY nome")
    formas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return formas

def adicionar_forma_pagamento(nome):
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO formas_pagamento (nome) VALUES (?)", (nome,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Forma de pagamento adicionada com sucesso!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"A forma de pagamento '{nome}' já existe.")
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
    finally:
        conn.close()

def excluir_forma_pagamento(nome):
    conn = conectar()
    if conn is None: return
    cursor = conn.cursor()
    padroes = ['Dinheiro', 'Cartão de Crédito', 'Cartão de Débito', 'Pix']
    if nome in padroes:
        messagebox.showwarning("Aviso", "Não é possível excluir formas de pagamento padrão.")
        return
    try:
        cursor.execute("DELETE FROM formas_pagamento WHERE nome = ?", (nome,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Forma de pagamento excluída com sucesso!")
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
    finally:
        conn.close()
