# 🐍 Sistema de Ponto de Venda (PDV) em Python

Este é um sistema de Ponto de Venda completo, desenvolvido em Python com a biblioteca Tkinter para a interface gráfica e SQLite para a base de dados. O projeto foi criado para simular um ambiente real de caixa de supermercado, incluindo funcionalidades de gestão e relatórios.

## ✨ Funcionalidades Principais

- **Módulo de Vendas (PDV):** Interface rápida para registo de produtos por código de barras, venda por unidade e por quilo (kg).
- **Gestão de Caixa:** Controlo de abertura, sangria e fecho de caixa.
- **Controlo de Operadores:** Sistema de login com níveis de acesso (Admin e Operador).
- **Gestão de Stock:** Cadastro, edição e exclusão de produtos.
- **Relatórios:** Visualização de vendas por período, formas de pagamento e produtos mais vendidos.
- **Impressão de Recibos:** Suporte para impressão de recibos não fiscais em impressoras térmicas.
- **Configuração Flexível:** Permite configurar dados da loja, impressora e formato de etiquetas de balança.

## 🚀 Como Executar

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
    cd SEU_REPOSITORIO
    ```
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Execute o módulo de gestão para configurar (como Admin: `admin`/`admin`):**
    ```bash
    python src/pdv_gestao.py
    ```
5.  **Execute o módulo de vendas para operar o caixa:**
    ```bash
    python src/pdv_vendas.py
    ```

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3
- **Interface Gráfica:** Tkinter
- **Base de Dados:** SQLite 3
- **Bibliotecas:** `python-escpos`, `matplotlib`, `tkcalendar`
