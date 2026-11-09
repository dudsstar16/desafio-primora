# 🔌 Guia Rápido para a Equipe da API (Django) — Como Acessar o Banco Pronto

Olá, equipe da **Parte 2 (API Django)**!  
A equipe de **ETL (Parte 1)** já limpou, padronizou e salvou todas as tabelas para vocês. **Vocês não precisam tratar nenhum dado!**

---

## 📦 O que já está pronto para vocês usarem?

As **3 tabelas** exigidas pelo desafio já estão criadas e populadas com os **nomes exatos de colunas do PDF**:

1. **Tabela `vendedor` (5 registros):**
   - `id_vendedor` (PK)
   - `nome_vendedor`
2. **Tabela `cliente` (47 registros):**
   - `id_cliente` (PK - ex: `"CLI0001"`)
   - `razao_social`
   - `cnpj_normalizado` (Texto 14 dígitos, sem pontuação)
   - `telefone_normalizado` (Texto 10/11 dígitos, ex: `"61970855700"`)
   - `email`
   - `bairro_normalizado` (`"Águas Claras"`, `"Taguatinga"`, `"Vicente Pires"`, `"Guará"`, `"Não Informado"`)
   - `cep_normalizado` (Texto 8 dígitos ou `NULL`)
   - `cidade` (`"Brasília"`)
   - `uf` (`"DF"`)
   - `data_cadastro_normalizado` (`AAAA-MM-DD`)
   - `vendedor_id` (FK apontando para `vendedor.id_vendedor`)
3. **Tabela `auditoria_etl` (188 registros):**
   - ⚠️ **Atenção à regra do PDF:** Esta tabela deve ser registrada **apenas no Django Admin** e **NÃO deve ter rota pública na API**.

---

## 🚀 Como usar o Banco de Dados no seu computador (2 Opções Fáceis)

### Opção 1: Usar o Banco Pronto que já veio no GitHub (Mais Rápido — Zero Configuração!)
O arquivo **`data/processed/banco_primora.sqlite3`** já está no repositório com todas as 3 tabelas populadas.  
No `settings.py` do Django, a configuração deve apontar para o caminho real do arquivo. Exemplo:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "data" / "processed" / "banco_primora.sqlite3",
    }
}
```
O exemplo considera que o projeto Django está dentro da pasta `api/`. Ajuste o caminho se a estrutura mudar.

Também será necessário criar models com os mesmos nomes de tabelas e colunas. Use `db_table` para ligar cada model à tabela existente. Decidam com a equipe se o Django administrará essas tabelas ou se os models usarão `managed = False`.

### Opção 2: Carregar no PostgreSQL
Esta opção exige que o PostgreSQL esteja instalado e que um banco vazio ou de teste já tenha sido criado. O script apaga tabelas existentes chamadas `auditoria_etl`, `cliente` e `vendedor` antes de recriá-las. Faça backup se o banco já tiver dados. Depois, execute o arquivo **`scripts/carga_postgresql.sql`**:
- **Pelo terminal:**
  ```bash
  psql -U postgres -d nome_do_seu_banco -f scripts/carga_postgresql.sql
  ```
- **Ou pelo pgAdmin 4:** Entre no banco escolhido, abra a *Query Tool*, carregue o arquivo `scripts/carga_postgresql.sql` e clique em **Play (Execute)**. O script cria as 3 tabelas e insere os dados.

---

## 👀 Quer ver as tabelas agora mesmo no navegador?
Dê 2 cliques no arquivo **`data/processed/visualizar_tabelas.html`**! Ele abre uma página bonita mostrando todos os vendedores, clientes e logs de auditoria.

