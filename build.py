import PyInstaller.__main__
import os

# --- Configurações ---
NOME_PDV_VENDAS = "PDV_Vendas"
NOME_PDV_GESTAO = "PDV_Gestao"
PASTA_ICONE = "assets"
NOME_ICONE = "dd_infomatica.ico"
PASTA_CODIGO = "src"
PASTA_HOOKS = "hooks"

# --- Construção do PDV de Vendas ---
print(f"--- Iniciando a criação do {NOME_PDV_VENDAS}.exe ---")
PyInstaller.__main__.run([
    '--noconsole',
    '--onefile',
    f'--name={NOME_PDV_VENDAS}',
    f'--icon={os.path.join(PASTA_ICONE, NOME_ICONE)}',
    f'--additional-hooks-dir={PASTA_HOOKS}', # Garante que ele lê os hooks
    os.path.join(PASTA_CODIGO, 'pdv_vendas.py'),
])
print(f"--- {NOME_PDV_VENDAS}.exe criado com sucesso! ---")

# --- Construção do PDV de Gestão ---
print(f"\n--- Iniciando a criação do {NOME_PDV_GESTAO}.exe ---")
PyInstaller.__main__.run([
    '--noconsole',
    '--onefile',
    f'--name={NOME_PDV_GESTAO}',
    f'--icon={os.path.join(PASTA_ICONE, NOME_ICONE)}',
    f'--additional-hooks-dir={PASTA_HOOKS}', # Garante que ele lê os hooks
    os.path.join(PASTA_CODIGO, 'pdv_gestao.py'),
])
print(f"--- {NOME_PDV_GESTAO}.exe criado com sucesso! ---")

print("\n\nProcesso concluído! Verifique a pasta 'dist'.")