"""
Etapa 6B do ETL: Orquestrador Completo do Pipeline (`python -m etl.pipeline`)
Executa Extração -> Transformação -> Auditoria -> Carga em 1 único comando!
"""
from collections import Counter
from etl.extract import extract_raw_clients
from etl.transform_fields import normalize_cnpj, normalize_phone, normalize_date
from etl.cep_service import CepService
from etl.transform_address import resolve_address
from etl.audit import AuditLogger
from etl.load import (
    save_csv_files,
    save_sqlite_database,
    generate_postgres_sql_script,
    try_load_into_postgresql,
    generate_html_viewer,
)


def run_pipeline() -> dict:
    print("🚀 [1/4] Extraindo dados brutos do CSV...")
    raw_rows = extract_raw_clients()

    print("🧹 [2/4] Transformando dados, consultando CEPs (com cache) e aplicando Guardrails...")
    cep_service = CepService()
    audit_logger = AuditLogger()

    # 1. Monta a tabela de Vendedores únicos (ordenados por nome)
    unique_vendedores = sorted(
        {r["vendedor_responsavel"].strip() for r in raw_rows if r.get("vendedor_responsavel")}
    )
    vendedores_table = [
        {"id_vendedor": idx, "nome_vendedor": nome}
        for idx, nome in enumerate(unique_vendedores, start=1)
    ]
    vendedor_name_to_id = {v["nome_vendedor"]: v["id_vendedor"] for v in vendedores_table}

    # 2. Processa os 47 Clientes e grava a Auditoria
    clientes_table = []
    for row in raw_rows:
        cid = row["id_cliente"]

        cnpj_clean, cnpj_rule = normalize_cnpj(row["cnpj"])
        audit_logger.log_change(cid, "cnpj", row["cnpj"], cnpj_clean, cnpj_rule)

        phone_clean, phone_rule = normalize_phone(row["telefone"])
        audit_logger.log_change(cid, "telefone", row["telefone"], phone_clean, phone_rule)

        date_clean, date_rule = normalize_date(row["data_cadastro"])
        audit_logger.log_change(cid, "data_cadastro", row["data_cadastro"], date_clean, date_rule)

        addr = resolve_address(row["bairro_informado"], row["cep"], cep_service)
        audit_logger.log_change(cid, "cep", row["cep"], addr["cep_normalizado"], addr["regra_cep"])
        audit_logger.log_change(
            cid, "bairro", row["bairro_informado"], addr["bairro_normalizado"], addr["regra_bairro"]
        )

        clientes_table.append(
            {
                "id_cliente": cid,
                "razao_social": row["razao_social"].strip(),
                "cnpj_normalizado": cnpj_clean,
                "telefone_normalizado": phone_clean,
                "email": row["email"].strip(),
                "bairro_normalizado": addr["bairro_normalizado"],
                "cep_normalizado": addr["cep_normalizado"],
                "cidade": row.get("cidade", "Brasília").strip() or "Brasília",
                "uf": row.get("uf", "DF").strip() or "DF",
                "data_cadastro_normalizado": date_clean,
                "vendedor_id": vendedor_name_to_id[row["vendedor_responsavel"].strip()],
            }
        )

    auditoria_table = [
        {"id_auditoria": idx, **entry}
        for idx, entry in enumerate(audit_logger.to_dicts(), start=1)
    ]

    print("💾 [3/4] Carregando tabelas no Banco de Dados e gerando artefatos para a equipe da API...")
    save_csv_files(vendedores_table, clientes_table, auditoria_table)
    sqlite_path = save_sqlite_database(vendedores_table, clientes_table, auditoria_table)
    sql_path = generate_postgres_sql_script(vendedores_table, clientes_table, auditoria_table)
    html_path = generate_html_viewer(vendedores_table, clientes_table, auditoria_table)
    pg_ok, pg_msg = try_load_into_postgresql(sql_path)

    bairros_count = Counter(c["bairro_normalizado"] for c in clientes_table)
    print("\n✅ [4/4] PIPELINE ETL CONCLUÍDO COM SUCESSO!")
    print(f"   • Vendedores carregados: {len(vendedores_table)}")
    print(f"   • Clientes tratados:     {len(clientes_table)}")
    print(f"   • Registros auditoria:   {len(auditoria_table)}")
    print(f"   • Resumo por Bairro:     {dict(bairros_count)}")
    print(f"   • Banco pronto (SQLite): {sqlite_path.relative_to(sqlite_path.parent.parent.parent)}")
    print(f"   • Script PostgreSQL:     {sql_path.relative_to(sql_path.parent.parent)}")
    print(f"   • Visualizador HTML:     {html_path.relative_to(html_path.parent.parent.parent)}")
    print(f"   • Status PostgreSQL:     {pg_msg}")

    return {
        "vendedores": vendedores_table,
        "clientes": clientes_table,
        "auditoria": auditoria_table,
        "pg_loaded": pg_ok,
    }


if __name__ == "__main__":
    run_pipeline()

