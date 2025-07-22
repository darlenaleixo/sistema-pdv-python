# impressao.py
from escpos.printer import Usb
from tkinter import messagebox
from configuracao import carregar_configuracoes
import banco
from datetime import datetime

def formatar_item(nome, qtd, preco_unit, subtotal, unidade):
    """Formata uma linha de item para o recibo, com alinhamento."""
    max_len = 48  # Largura padrão para impressoras de 80mm
    
    # Linha 1: Quantidade e Nome
    if unidade == 'un':
        qtd_str = f"{int(qtd)}{unidade}"
    else:
        qtd_str = f"{qtd:.3f}{unidade}"
    
    nome_curto = (nome[:25] + '...') if len(nome) > 28 else nome
    linha1 = f"{qtd_str} {nome_curto}"
    
    # Linha 2: Preço unitário e subtotal
    preco_str = f"R$ {preco_unit:.2f}"
    subtotal_str = f"R$ {subtotal:.2f}"
    espacos = max_len - len(preco_str) - len(subtotal_str)
    linha2 = f"{preco_str}{' ' * espacos}{subtotal_str}\n"
    
    return linha1 + '\n' + linha2

def imprimir_recibo(venda_id, total, forma_pagamento, troco, itens, operador_nome):
    """Gera e imprime o recibo para uma venda específica."""
    config = carregar_configuracoes()
    vendor_id = config.get("impressora_vendor_id")
    product_id = config.get("impressora_product_id")

    if not vendor_id or not product_id:
        messagebox.showwarning("Impressora não Configurada", "Nenhuma impressora foi configurada. Vá em Gerenciar > Configurações.")
        return

    try:
        p = Usb(int(vendor_id, 16), int(product_id, 16), timeout=0, in_ep=0x81, out_ep=0x03)
        
        # --- Cabeçalho ---
        p.set(align='center', text_type='B', width=2, height=2)
        p.text(config.get("loja_nome", "") + "\n")
        p.set(align='center', text_type='NORMAL')
        p.text(config.get("loja_endereco", "") + "\n")
        p.text(config.get("loja_telefone_cnpj", "") + "\n")
        p.text("-" * 48 + "\n")
        p.text("CUPOM NAO FISCAL\n")
        p.text("-" * 48 + "\n")

        # --- Itens ---
        p.set(align='left')
        for item in itens:
            # item: [codigo, nome, qtd, preco_unit, subtotal, unidade]
            linha = formatar_item(item[1], item[2], item[3], item[4], item[5])
            p.text(linha)
        
        p.text("-" * 48 + "\n")

        # --- Rodapé ---
        p.set(align='right', text_type='B')
        p.text(f"TOTAL: R$ {total:.2f}\n")
        p.set(align='right', text_type='NORMAL')
        p.text(f"Pagamento: {forma_pagamento}\n")
        if forma_pagamento == "Dinheiro" and troco > 0:
            p.text(f"Troco: R$ {troco:.2f}\n")
        
        p.text("\n")
        p.set(align='center')
        p.text(f"Operador: {operador_nome}\n")
        p.text(f"Venda: #{venda_id} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        p.text("Obrigado e volte sempre!\n")
        
        # --- Finalização ---
        p.cut()
        p.close()
        
        messagebox.showinfo("Impressão", "Recibo enviado para a impressora.")

    except Exception as e:
        messagebox.showerror("Erro de Impressão", f"Não foi possível imprimir o recibo:\n{e}")
