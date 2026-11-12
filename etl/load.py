"""
Etapa 6A do ETL: Carga dos Dados (Load)
Salva as 3 tabelas prontas (`vendedor`, `cliente`, `auditoria_etl`) em:
1. Banco de dados pronto no repositório (`data/processed/banco_primora.sqlite3`) — colegas abrem direto sem instalar nada!
2. PostgreSQL (local ou em nuvem via `.env`) + Script SQL automático (`scripts/carga_postgresql.sql`).
3. Planilhas CSV limpas (`data/processed/*.csv`) + Painel Visual HTML (`data/processed/visualizar_tabelas.html`).
"""
import csv
import html
import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SCRIPTS_DIR = BASE_DIR / "scripts"


def save_csv_files(
    vendedores: list[dict[str, Any]],
    clientes: list[dict[str, Any]],
    auditoria: list[dict[str, Any]],
) -> None:
    """Salva as 3 tabelas como arquivos CSV limpos em `data/processed/`."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    def _write(filename: str, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
        path = PROCESSED_DIR / filename
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for r in rows:
                writer.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fieldnames})

    _write("vendedores_limpos.csv", vendedores, ["id_vendedor", "nome_vendedor"])
    _write(
        "clientes_limpos.csv",
        clientes,
        [
            "id_cliente",
            "razao_social",
            "cnpj_normalizado",
            "telefone_normalizado",
            "email",
            "bairro_normalizado",
            "cep_normalizado",
            "cidade",
            "uf",
            "data_cadastro_normalizado",
            "vendedor_id",
        ],
    )
    _write(
        "auditoria_etl.csv",
        auditoria,
        [
            "id_auditoria",
            "id_cliente",
            "campo_afetado",
            "valor_original",
            "valor_tratado",
            "regra_aplicada",
            "data_processamento",
        ],
    )


def save_sqlite_database(
    vendedores: list[dict[str, Any]],
    clientes: list[dict[str, Any]],
    auditoria: list[dict[str, Any]],
    db_path: Path = PROCESSED_DIR / "banco_primora.sqlite3",
) -> Path:
    """
    Cria o banco de dados relacional pronto em arquivo (`banco_primora.sqlite3`).
    Quando subir para o GitHub, qualquer colega que fizer `git pull` já recebe
    o banco com as 3 tabelas populadas e prontas para o Django usar!
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE vendedor (
            id_vendedor INTEGER PRIMARY KEY,
            nome_vendedor VARCHAR(100) NOT NULL UNIQUE
        );

        CREATE TABLE cliente (
            id_cliente VARCHAR(20) PRIMARY KEY,
            razao_social VARCHAR(150) NOT NULL,
            cnpj_normalizado VARCHAR(14) NOT NULL,
            telefone_normalizado VARCHAR(11) NOT NULL,
            email VARCHAR(150) NOT NULL,
            bairro_normalizado VARCHAR(100) NOT NULL,
            cep_normalizado VARCHAR(8),
            cidade VARCHAR(50) NOT NULL,
            uf VARCHAR(2) NOT NULL,
            data_cadastro_normalizado DATE NOT NULL,
            vendedor_id INTEGER NOT NULL REFERENCES vendedor(id_vendedor)
        );

        CREATE TABLE auditoria_etl (
            id_auditoria INTEGER PRIMARY KEY,
            id_cliente VARCHAR(20) NOT NULL REFERENCES cliente(id_cliente),
            campo_afetado VARCHAR(50) NOT NULL,
            valor_original TEXT,
            valor_tratado TEXT,
            regra_aplicada VARCHAR(150) NOT NULL,
            data_processamento TIMESTAMP NOT NULL
        );
        """
    )

    cur.executemany(
        "INSERT INTO vendedor (id_vendedor, nome_vendedor) VALUES (:id_vendedor, :nome_vendedor)",
        vendedores,
    )
    cur.executemany(
        """
        INSERT INTO cliente (
            id_cliente, razao_social, cnpj_normalizado, telefone_normalizado,
            email, bairro_normalizado, cep_normalizado, cidade, uf,
            data_cadastro_normalizado, vendedor_id
        ) VALUES (
            :id_cliente, :razao_social, :cnpj_normalizado, :telefone_normalizado,
            :email, :bairro_normalizado, :cep_normalizado, :cidade, :uf,
            :data_cadastro_normalizado, :vendedor_id
        )
        """,
        clientes,
    )
    cur.executemany(
        """
        INSERT INTO auditoria_etl (
            id_auditoria, id_cliente, campo_afetado, valor_original,
            valor_tratado, regra_aplicada, data_processamento
        ) VALUES (
            :id_auditoria, :id_cliente, :campo_afetado, :valor_original,
            :valor_tratado, :regra_aplicada, :data_processamento
        )
        """,
        auditoria,
    )

    conn.commit()
    conn.close()
    return db_path


def generate_postgres_sql_script(
    vendedores: list[dict[str, Any]],
    clientes: list[dict[str, Any]],
    auditoria: list[dict[str, Any]],
    sql_path: Path = SCRIPTS_DIR / "carga_postgresql.sql",
) -> Path:
    """
    Gera o script SQL completo e compatível com PostgreSQL (`scripts/carga_postgresql.sql`).
    Cria as 3 tabelas e insere todos os registros de uma vez.
    """
    sql_path.parent.mkdir(parents=True, exist_ok=True)

    def _sql_val(val: Any) -> str:
        if val is None:
            return "NULL"
        if isinstance(val, int):
            return str(val)
        escaped = str(val).replace("'", "''")
        return f"'{escaped}'"

    lines = [
        "-- =====================================================================",
        "-- SCRIPT AUTOMÁTICO DE CRIAÇÃO E CARGA (POSTGRESQL) — DESAFIO PRIMORA",
        "-- Tabelas: vendedor, cliente, auditoria_etl",
        "-- =====================================================================",
        "",
        "BEGIN;",
        "",
        "DROP TABLE IF EXISTS auditoria_etl CASCADE;",
        "DROP TABLE IF EXISTS cliente CASCADE;",
        "DROP TABLE IF EXISTS vendedor CASCADE;",
        "",
        "-- 1. Tabela de Vendedores",
        "CREATE TABLE vendedor (",
        "    id_vendedor SERIAL PRIMARY KEY,",
        "    nome_vendedor VARCHAR(100) NOT NULL UNIQUE",
        ");",
        "",
        "-- 2. Tabela de Clientes (Nomes de colunas idênticos à especificação da API)",
        "CREATE TABLE cliente (",
        "    id_cliente VARCHAR(20) PRIMARY KEY,",
        "    razao_social VARCHAR(150) NOT NULL,",
        "    cnpj_normalizado VARCHAR(14) NOT NULL,",
        "    telefone_normalizado VARCHAR(11) NOT NULL,",
        "    email VARCHAR(150) NOT NULL,",
        "    bairro_normalizado VARCHAR(100) NOT NULL,",
        "    cep_normalizado VARCHAR(8) NULL,",
        "    cidade VARCHAR(50) NOT NULL DEFAULT 'Brasília',",
        "    uf VARCHAR(2) NOT NULL DEFAULT 'DF',",
        "    data_cadastro_normalizado DATE NOT NULL,",
        "    vendedor_id INTEGER NOT NULL REFERENCES vendedor(id_vendedor)",
        ");",
        "",
        "-- 3. Tabela de Auditoria do ETL (Apenas no Admin, não exposta na API)",
        "CREATE TABLE auditoria_etl (",
        "    id_auditoria SERIAL PRIMARY KEY,",
        "    id_cliente VARCHAR(20) NOT NULL REFERENCES cliente(id_cliente),",
        "    campo_afetado VARCHAR(50) NOT NULL,",
        "    valor_original TEXT NULL,",
        "    valor_tratado TEXT NULL,",
        "    regra_aplicada VARCHAR(150) NOT NULL,",
        "    data_processamento TIMESTAMP NOT NULL",
        ");",
        "",
        "-- Inserindo Vendedores",
    ]

    for v in vendedores:
        lines.append(
            f"INSERT INTO vendedor (id_vendedor, nome_vendedor) VALUES "
            f"({_sql_val(v['id_vendedor'])}, {_sql_val(v['nome_vendedor'])});"
        )

    lines.append("")
    lines.append("-- Inserindo 47 Clientes Limpos e Padronizados")
    for c in clientes:
        lines.append(
            "INSERT INTO cliente (id_cliente, razao_social, cnpj_normalizado, telefone_normalizado, "
            "email, bairro_normalizado, cep_normalizado, cidade, uf, data_cadastro_normalizado, vendedor_id) VALUES ("
            f"{_sql_val(c['id_cliente'])}, {_sql_val(c['razao_social'])}, {_sql_val(c['cnpj_normalizado'])}, "
            f"{_sql_val(c['telefone_normalizado'])}, {_sql_val(c['email'])}, {_sql_val(c['bairro_normalizado'])}, "
            f"{_sql_val(c['cep_normalizado'])}, {_sql_val(c['cidade'])}, {_sql_val(c['uf'])}, "
            f"{_sql_val(c['data_cadastro_normalizado'])}, {_sql_val(c['vendedor_id'])});"
        )

    lines.append("")
    lines.append("-- Inserindo Registros de Auditoria do ETL")
    for a in auditoria:
        lines.append(
            "INSERT INTO auditoria_etl (id_auditoria, id_cliente, campo_afetado, valor_original, "
            "valor_tratado, regra_aplicada, data_processamento) VALUES ("
            f"{_sql_val(a['id_auditoria'])}, {_sql_val(a['id_cliente'])}, {_sql_val(a['campo_afetado'])}, "
            f"{_sql_val(a['valor_original'])}, {_sql_val(a['valor_tratado'])}, "
            f"{_sql_val(a['regra_aplicada'])}, {_sql_val(a['data_processamento'])});"
        )

    lines.extend([
        "",
        "-- Ajusta contadores sequenciais do PostgreSQL",
        "SELECT setval('vendedor_id_vendedor_seq', (SELECT MAX(id_vendedor) FROM vendedor));",
        "SELECT setval('auditoria_etl_id_auditoria_seq', (SELECT MAX(id_auditoria) FROM auditoria_etl));",
        "",
        "COMMIT;",
    ])

    sql_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sql_path


def try_load_into_postgresql(sql_script_path: Path) -> tuple[bool, str]:
    """
    Se houver configuração de PostgreSQL no ambiente (variável DATABASE_URL,
    POSTGRES_PASSWORD ou DB_PASSWORD), conecta automaticamente via psycopg2
    e carrega as 3 tabelas no PostgreSQL!
    """
    db_url = os.getenv("DATABASE_URL")
    pg_password = os.getenv("POSTGRES_PASSWORD") or os.getenv("DB_PASSWORD")
    if not db_url and not pg_password:
        return False, "Variáveis de conexão PostgreSQL não definidas no .env (carga SQL e SQLite já geradas)."

    try:
        import psycopg2  # type: ignore

        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST") or os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT") or os.getenv("DB_PORT", "5432")),
                dbname=os.getenv("POSTGRES_DB") or os.getenv("DB_NAME", "primora_api"),
                user=os.getenv("POSTGRES_USER") or os.getenv("DB_USER", "postgres"),
                password=pg_password,
            )
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_script_path.read_text(encoding="utf-8"))
        conn.close()
        return True, "Dados carregados com sucesso diretamente no PostgreSQL!"
    except Exception as exc:
        return False, f"Aviso ao conectar no PostgreSQL: {exc}"


def generate_html_viewer(
    vendedores: list[dict[str, Any]],
    clientes: list[dict[str, Any]],
    auditoria: list[dict[str, Any]],
    html_path: Path = PROCESSED_DIR / "visualizar_tabelas.html",
) -> Path:
    """
    Cria um painel visual em HTML para qualquer pessoa do grupo abrir no navegador
    com 2 cliques e ver as 3 tabelas prontas sem precisar instalar programas!
    """
    html_path.parent.mkdir(parents=True, exist_ok=True)

    def _e(v: Any) -> str:
        return html.escape("" if v is None else str(v))

    vend_rows = "".join(
        f"<tr><td>{_e(v['id_vendedor'])}</td><td><strong>{_e(v['nome_vendedor'])}</strong></td></tr>"
        for v in vendedores
    )
    cli_rows = "".join(
        f"<tr>"
        f"<td><code>{_e(c['id_cliente'])}</code></td>"
        f"<td>{_e(c['razao_social'])}</td>"
        f"<td><code>{_e(c['cnpj_normalizado'])}</code></td>"
        f"<td><code>{_e(c['telefone_normalizado'])}</code></td>"
        f"<td>{_e(c['email'])}</td>"
        f"<td><span class='badge'>{_e(c['bairro_normalizado'])}</span></td>"
        f"<td><code>{_e(c['cep_normalizado'] or 'NULL')}</code></td>"
        f"<td>{_e(c['data_cadastro_normalizado'])}</td>"
        f"<td>{_e(c['vendedor_id'])}</td>"
        f"</tr>"
        for c in clientes
    )
    aud_rows = "".join(
        f"<tr>"
        f"<td>{_e(a['id_auditoria'])}</td>"
        f"<td><code>{_e(a['id_cliente'])}</code></td>"
        f"<td><strong>{_e(a['campo_afetado'])}</strong></td>"
        f"<td class='old'>{_e(a['valor_original'])}</td>"
        f"<td class='new'>{_e(a['valor_tratado'])}</td>"
        f"<td><code>{_e(a['regra_aplicada'])}</code></td>"
        f"</tr>"
        for a in auditoria
    )

    page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Visualizador das Tabelas do Banco — Desafio Primora</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
  h1 {{ margin-top: 0; color: #38bdf8; }}
  .cards {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ background: #1e293b; border: 1px solid #334155; padding: 16px 20px; border-radius: 10px; }}
  .card h3 {{ margin: 0 0 6px 0; font-size: 14px; color: #94a3b8; }}
  .card p {{ margin: 0; font-size: 24px; font-weight: 700; color: #f8fafc; }}
  h2 {{ color: #e2e8f0; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-top: 32px; }}
  .table-wrap {{ overflow-x: auto; background: #1e293b; border-radius: 10px; border: 1px solid #334155; max-height: 460px; overflow-y: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ position: sticky; top: 0; background: #0f172a; color: #38bdf8; text-align: left; padding: 10px 12px; border-bottom: 1px solid #334155; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #334155; }}
  tr:hover td {{ background: #334155; }}
  code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; color: #bae6fd; }}
  .badge {{ background: #0284c7; color: #fff; padding: 3px 8px; border-radius: 999px; font-weight: 600; font-size: 12px; }}
  .old {{ color: #fca5a5; }}
  .new {{ color: #86efac; font-weight: 600; }}
</style>
</head>
<body>
  <h1>🗄️ Banco de Dados Pronto — Distribuidora Vetor (Primora)</h1>
  <div class="cards">
    <div class="card"><h3>Tabela 1: vendedor</h3><p>{len(vendedores)} registros</p></div>
    <div class="card"><h3>Tabela 2: cliente</h3><p>{len(clientes)} registros</p></div>
    <div class="card"><h3>Tabela 3: auditoria_etl</h3><p>{len(auditoria)} logs gravados</p></div>
  </div>

  <h2>1. Tabela <code>vendedor</code> (5 Vendedores Responsáveis)</h2>
  <div class="table-wrap">
    <table>
      <thead><tr><th>id_vendedor (PK)</th><th>nome_vendedor</th></tr></thead>
      <tbody>{vend_rows}</tbody>
    </table>
  </div>

  <h2>2. Tabela <code>cliente</code> (47 Clientes Limpos e Padronizados)</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>id_cliente (PK)</th><th>razao_social</th><th>cnpj_normalizado (Texto)</th>
          <th>telefone_normalizado (Texto)</th><th>email</th><th>bairro_normalizado</th>
          <th>cep_normalizado</th><th>data_cadastro_normalizado</th><th>vendedor_id (FK)</th>
        </tr>
      </thead>
      <tbody>{cli_rows}</tbody>
    </table>
  </div>

  <h2>3. Tabela <code>auditoria_etl</code> (Histórico Completo de Tratamentos — Visível Apenas no Admin)</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>id_auditoria (PK)</th><th>id_cliente (FK)</th><th>campo_afetado</th>
          <th>valor_original (Antes)</th><th>valor_tratado (Depois)</th><th>regra_aplicada (Guardrail)</th>
        </tr>
      </thead>
      <tbody>{aud_rows}</tbody>
    </table>
  </div>
</body>
</html>
"""
    html_path.write_text(page, encoding="utf-8")
    return html_path

