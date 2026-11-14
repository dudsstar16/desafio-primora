import sqlite3

caminho = "data/processed/banco_primora.sqlite3"

conexao = sqlite3.connect(caminho)

consulta = """
SELECT name
FROM sqlite_master
WHERE type = 'table'
AND name = 'django_migrations';
"""

resultado = conexao.execute(consulta).fetchone()

if resultado:
    print("A tabela django_migrations existe.")
else:
    print("A tabela django_migrations não existe.")

conexao.close()