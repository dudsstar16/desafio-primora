# Desafio Técnico — Distribuidora Vetor (Primora)

![CI Status](https://github.com/dudsstar16/desafio-primora/actions/workflows/ci.yml/badge.svg)

Projeto integrado de Engenharia e Backend desenvolvido como parte do Desafio Primora.  
O objetivo é tratar dados cadastrais inconsistentes de clientes (ETL em Python), armazená-los em banco relacional (PostgreSQL) e disponibilizá-los através de uma API REST (Django REST Framework).

> 👉 **Primeira vez no repositório?**  
> Leia nosso guia super simples e direto para o grupo: **[COMECE_POR_AQUI.md](COMECE_POR_AQUI.md)**.
> 
> 📋 **Gestão Ágil e Sprints (Scrum / Trello):**  
> Acompanhe nossas tarefas, Sprints e Product Backlog no **[Quadro Oficial do Trello — Desafio Primora (IFB)](https://trello.com/b/EfR7pCde/desafio-primora-ifb-projeto-integrador)** e na aba **[Issues do GitHub](https://github.com/dudsstar16/desafio-primora/issues)**.

---

## 🎯 Objetivo do Projeto

A Distribuidora Vetor acumulou dados cadastrais ao longo dos anos com grafias inconsistentes de bairros, formatos variados de CNPJ, telefones e datas, além de CEPs faltantes ou conflitantes.

O desafio é dividido em duas frentes:
1. **Parte 1 (ETL e Limpeza de Dados):**
   - Construir um fluxo (pipeline) em Python para extrair, limpar, padronizar e enriquecer os dados.
   - Criar uma tabela de auditoria para registrar todas as alterações feitas.
   - Persistir os dados limpos em banco relacional PostgreSQL.
   - Desenvolver testes automatizados para validar as regras de limpeza.

2. **Parte 2 (API REST em Django):**
   - Disponibilizar endpoints para consulta e manutenção (CRUD) de clientes e vendedores.
   - Implementar regras de autenticação via Token.
   - Disponibilizar documentação OpenAPI / Redoc.

---

## 📁 Estrutura do Repositório

```text
desafio-primora/
│
├── docs/                   # Documentações gerais do projeto
│   ├── requisitos/         # PDFs e critérios oficiais do desafio
│   ├── arquitetura/        # Planejamento técnico e decisões arquiteturais
│   ├── modelagem/          # Modelos de banco de dados (MER e DER)
│   └── relatorios/         # Relatório técnico de decisões e trade-offs
│
├── data/                   # Armazenamento de dados
│   ├── raw/                # Arquivo CSV bruto original
│   └── processed/          # Banco, CSVs, cache e painel gerados pelo ETL
│
├── etl/                    # Scripts do pipeline de ETL em Python
│
├── api/                    # Aplicação web backend em Django e Django REST Framework
│
├── tests/                  # Testes automatizados (pytest)
│
├── scripts/                # Scripts auxiliares e migrações SQL
│
├── .gitignore              # Arquivos e pastas ignorados pelo controle de versão Git
├── COMECE_POR_AQUI.md      # Guia rápido e simples para todos os integrantes
├── README.md               # Documentação inicial e guia do projeto
└── requirements.txt        # Dependências e bibliotecas do projeto
```

### Finalidade das Pastas

| Pasta | Finalidade |
| :--- | :--- |
| `docs/requisitos` | PDFs e critérios oficiais do desafio |
| `docs/arquitetura` | Planejamento técnico e fluxogramas |
| `docs/modelagem` | MER (Modelo Entidade-Relacionamento) e DER (Diagrama) |
| `docs/relatorios` | Relatório de decisões e trade-offs (escolhas técnicas) |
| `data/raw` | CSV original fornecido pela empresa |
| `data/processed` | Banco SQLite, CSVs limpos, auditoria, cache de CEP e painel HTML |
| `etl` | Pipeline em Python: extração, limpeza, auditoria e carga |
| `api` | Projeto Django e endpoints da API REST (`vendedores`, `clientes` e autenticação) |
| `tests` | Testes automatizados das regras de limpeza e dos conflitos de CEP |
| `scripts` | Script pronto para carregar as tabelas no PostgreSQL |
| `.github/workflows` | Automação CI/CD (GitHub Actions) que executa os testes do ETL e da API a cada Push/PR |

---

## 🗂️ Rastreabilidade das Etapas do ETL (Mapeamento Trello ↔ Repositório)

Cada cartão do nosso **[Quadro Scrum no Trello](https://trello.com/b/EfR7pCde/desafio-primora-ifb-projeto-integrador)** corresponde diretamente aos módulos e documentos entregues neste repositório:

| Etapa / Cartão no Trello | Código e Documentação Comprobatória no Repositório | Status |
| :--- | :--- | :---: |
| **1. Desenhar como o projeto vai funcionar** | [`README.md`](README.md), [`COMECE_POR_AQUI.md`](COMECE_POR_AQUI.md), [`docs/arquitetura/regras_negocio_etl.md`](docs/arquitetura/regras_negocio_etl.md) | ✅ Concluído |
| **2. ETL - Planejar como guardar os dados** | [`docs/modelagem/mer_der.md`](docs/modelagem/mer_der.md), [`docs/arquitetura/guia_banco_para_equipe_api.md`](docs/arquitetura/guia_banco_para_equipe_api.md) | ✅ Concluído |
| **3. ETL - Preparar e realizar extração dos dados** | [`etl/extract.py`](etl/extract.py), [`data/raw/02-clientes_distribuidora_vetor.csv`](data/raw/02-clientes_distribuidora_vetor.csv) | ✅ Concluído |
| **4. ETL - Identificar e normalizar inconsistências** | [`etl/transform_fields.py`](etl/transform_fields.py), [`etl/transform_address.py`](etl/transform_address.py), [`data/processed/clientes_limpos.csv`](data/processed/clientes_limpos.csv) | ✅ Concluído |
| **5. ETL - Validar e enriquecer informações de CEP** | [`etl/cep_service.py`](etl/cep_service.py), [`data/processed/cep_cache.json`](data/processed/cep_cache.json) | ✅ Concluído |
| **6. ETL - Implementar auditoria das transformações** | [`etl/audit.py`](etl/audit.py), [`data/processed/auditoria_etl.csv`](data/processed/auditoria_etl.csv) (188 registros) | ✅ Concluído |
| **7. ETL - Desenvolver e executar o pipeline ETL** | [`etl/pipeline.py`](etl/pipeline.py), [`etl/load.py`](etl/load.py), [`data/processed/banco_primora.sqlite3`](data/processed/banco_primora.sqlite3), [`scripts/carga_postgresql.sql`](scripts/carga_postgresql.sql), [`data/processed/visualizar_tabelas.html`](data/processed/visualizar_tabelas.html) | ✅ Concluído |
| **8. ETL - Testar e documentar o processo ETL** | [`tests/test_etl.py`](tests/test_etl.py), [`.github/workflows/ci.yml`](.github/workflows/ci.yml), [`docs/relatorios/relatorio_tradeoffs_etl.md`](docs/relatorios/relatorio_tradeoffs_etl.md) | ✅ Concluído |

---

## ✅ Etapa 6 — Entregáveis do ETL

O comando `python -m etl.pipeline` lê a base original e gera os arquivos abaixo.

| Arquivo | Para que serve | Como usar |
| :--- | :--- | :--- |
| `data/processed/visualizar_tabelas.html` | Mostra as 3 tabelas em um painel visual. | Dê dois cliques e abra no Chrome ou Edge. |
| `data/processed/banco_primora.sqlite3` | Banco pronto com 5 vendedores, 47 clientes e 188 registros de auditoria. | Aponte o Django para esse arquivo. Não precisa instalar um servidor de banco. |
| `scripts/carga_postgresql.sql` | Recria e preenche as mesmas 3 tabelas no PostgreSQL. | Execute somente em banco vazio ou de teste. O script apaga tabelas existentes com os mesmos nomes. |
| `data/processed/clientes_limpos.csv` | Tabela de clientes já tratada. | Abra no Excel, LibreOffice ou em outro programa que leia CSV. |
| `data/processed/vendedores_limpos.csv` | Tabela de vendedores sem duplicações. | Abra no Excel, LibreOffice ou em outro programa que leia CSV. |
| `data/processed/auditoria_etl.csv` | Histórico das mudanças feitas pelo ETL. | Use para conferir o valor anterior, o novo valor e a regra aplicada. |
| `data/processed/cep_cache.json` | Guarda respostas de CEP já consultadas. | O pipeline usa automaticamente para evitar consultas repetidas. |
| `docs/arquitetura/guia_banco_para_equipe_api.md` | Explica como conectar o Django ao banco. | Leia antes de iniciar os models e o Django Admin. |
| `docs/arquitetura/regras_negocio_etl.md` | Explica as regras de limpeza. | Consulte para entender por que cada dado foi alterado. |
| `docs/modelagem/mer_der.md` | Mostra as tabelas e os relacionamentos. | Use como referência para criar os models. |
| `docs/relatorios/relatorio_tradeoffs_etl.md` | Resume decisões, limites, cache e guardrail de conflito. | Use na revisão da equipe e na apresentação para a banca. |

> **Regra importante:** `auditoria_etl` deve aparecer somente no Django Admin. Ela não deve ter rota pública na API.

> **Atenção:** antes de usar o script PostgreSQL em um banco com dados, faça backup. O arquivo executa `DROP TABLE` para substituir as tabelas `vendedor`, `cliente` e `auditoria_etl`.

---

## 📋 Checklist de Entrega

### Etapa 1 — Preparação do Repositório
- [x] Criar o repositório privado
- [x] Adicionar `.gitignore` configurado
- [x] Adicionar `README.md` estruturado
- [x] Criar a estrutura completa de pastas do projeto
- [x] Adicionar os três PDFs de especificação em `docs/requisitos/`
- [x] Adicionar a base original `02-clientes_distribuidora_vetor.csv` em `data/raw/`
- [x] Convidar os integrantes do grupo para o repositório no GitHub

### Parte 1 — ETL
- [x] **Etapa 2:** Modelagem do banco e planejamento da auditoria.
- [x] **Etapa 3:** Pipeline de limpeza de bairros, CEPs, CNPJ, telefone e datas.
- [x] **Etapa 4:** Testes automatizados com chamadas de CEP simuladas.
- [x] **Etapa 5:** Geração das tabelas em SQLite, CSV e script PostgreSQL.
- [x] **Etapa 6:** Documentação, painel visual e relatório de decisões.

### Parte 2 — API REST em Django (100% Concluída!)
- [x] Criar o projeto Django base e configurar integração com o banco do ETL (`SQLite` / `PostgreSQL`).
- [x] Implementar módulo e CRUD de Vendedores (`/api/vendedores/`), autenticação por Token (`/api/auth/token/`), permissão global `IsAuthenticatedOrReadOnly`, registro no Admin e testes automatizados (PR #1 — `@alderiana`).
- [x] Implementar Model, Serializer e CRUD de Clientes (`/api/clientes/`) e rotas de filtro por bairro (`/api/clientes/bairro/{nome}/`) e por vendedor (`/api/clientes/vendedor/{id}/` e `/api/vendedores/{id}/clientes/`) (PR #9 — `@Hefestos27`).
- [x] Registrar `Vendedor`, `Cliente` e `AuditoriaEtl` no Django Admin (mantendo `auditoria_etl` restrita ao Admin e fora das rotas públicas da API).
- [x] Publicar a documentação interativa OpenAPI, Redoc (`/api/docs/`) e Swagger (`/api/swagger/`) com `drf-spectacular`.

---

## 🛠️ Como Configurar o Ambiente de Desenvolvimento

### 1. Pré-requisitos
- **Python 3.10+** instalado
- **Git** instalado
- **PostgreSQL** instalado e em execução (para etapas futuras)

### 2. Clonar o Repositório
```bash
git clone https://github.com/<seu-usuario>/desafio-primora.git
cd desafio-primora
```

### 3. Criar e Ativar o Ambiente Virtual

> #### 💡 Para que serve o Ambiente Virtual (`venv`) e por que ativá-lo?
> - **O que é:** Uma caixa isolada só para este projeto.
> - **Por que criar:** Evita misturar os pacotes deste projeto com outros programas do seu computador. Garante que todos no grupo usem exatamente as mesmas versões.
> - **Por que ATIVAR:** O comando de ativação avisa ao seu terminal: *"A partir de agora, use o Python e o pip desta pasta, e não os globais do Windows"*.
> - **Como saber se deu certo:** Um `(venv)` vai aparecer no comecinho da linha do seu terminal.

**No Windows (PowerShell):**
```powershell
# Cria a caixinha isolada chamada venv
python -m venv venv

# Ativa o ambiente (liga a chavinha no terminal)
.\venv\Scripts\Activate.ps1
```

> **Dica Windows:** Se der erro de script bloqueado, execute antes:  
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

**No Linux/Mac:**
```bash
# Cria a caixinha isolada chamada venv
python3 -m venv venv

# Ativa o ambiente
source venv/bin/activate
```

### 4. Instalar as Dependências
Com o ambiente ativado `(venv)`, instale as bibliotecas necessárias:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Como Executar o Projeto (ETL, Servidor da API e Testes)

### 1. Como Rodar o Pipeline de ETL (Parte 1)
Para reprocessar a planilha original (`data/raw/02-clientes_distribuidora_vetor.csv`), aplicar todas as regras de limpeza, consultar o cache de CEP e regerar o banco e as tabelas tratadas:
```bash
python -m etl.pipeline
```
- **Visualização rápida sem servidor:** Dê 2 cliques no arquivo `data/processed/visualizar_tabelas.html` para ver as 3 tabelas (`vendedor`, `cliente`, `auditoria_etl`) no navegador.

---

### 2. Como Rodar o Servidor da API em Django (Parte 2)

> **💡 Conexão Automática de Banco:**  
> Por padrão, o Django já abre automaticamente o banco **`data/processed/banco_primora.sqlite3`** gerado pelo ETL (com os 5 vendedores, 47 clientes e 188 logs de auditoria prontos!). Se desejar usar **PostgreSQL**, basta preencher o arquivo `.env` seguindo o exemplo de `api/.env.example` e executar `scripts/carga_postgresql.sql`.

**Passo A — Preparar as tabelas internas do Django (Login/Admin):**
```bash
python api/manage.py migrate --fake-initial
```
*(O comando `--fake-initial` avisa ao Django para aproveitar as tabelas `vendedor`, `cliente` e `auditoria_etl` que o ETL já criou!)*

**Passo B — (Opcional) Criar um usuário Administrador para entrar no Painel Admin:**
```bash
python api/manage.py createsuperuser
```

**Passo C — Ligar o Servidor da API:**
```bash
python api/manage.py runserver
```

---

### 🌐 3. Rotas Disponíveis para Testar no Navegador (`http://127.0.0.1:8000`)

Com o servidor ligado (`runserver`), acesse qualquer um dos endereços abaixo:

| Rota / Endpoint | O que faz | Permissão |
| :--- | :--- | :--- |
| **`/api/docs/`** | **Documentação Interativa Redoc** (manual visual completo da API) | Pública |
| **`/api/swagger/`** | **Documentação Swagger UI** (permite testar as rotas clicando na tela) | Pública |
| **`/api/clientes/`** | Lista todos os 47 clientes tratados (`GET`) ou cadastra novo (`POST`) | `GET` Público / `POST` Token |
| **`/api/clientes/{id}/`** | Detalhes de um cliente específico (ex: `/api/clientes/CLI0001/`) | `GET` Público / Edição Token |
| **`/api/clientes/bairro/{nome}/`** | Filtra clientes por bairro com ou sem acento (ex: `/api/clientes/bairro/aguas claras/`) | Pública (`GET`) |
| **`/api/clientes/vendedor/{id}/`** | Lista clientes atendidos por um vendedor (ex: `/api/clientes/vendedor/1/`) | Pública (`GET`) |
| **`/api/vendedores/`** | Lista os 5 vendedores (`GET`) ou cadastra novo (`POST`) | `GET` Público / `POST` Token |
| **`/api/vendedores/{id}/clientes/`** | Lista todos os clientes daquele vendedor (ex: `/api/vendedores/1/clientes/`) | Pública (`GET`) |
| **`/api/auth/token/`** | Envia `username` e `password` via `POST` e recebe o Token de autenticação | Pública (`POST`) |
| **`/admin/`** | **Painel Administrativo Django** (acesso às 3 tabelas, incluindo **`Auditoria do ETL`**) | Restrito (Login Admin) |

---

### 🧪 4. Como Rodar os 20 Testes Automatizados

Nosso projeto possui **20 testes automatizados** (também executados automaticamente a cada envio pelo **GitHub Actions**):

```bash
# 1. Rodar os 7 testes do Pipeline ETL (com simulação Mock da API de CEP):
python -m unittest discover -s tests -v

# 2. Rodar os 13 testes da API Django (8 de Vendedores + 5 de Clientes e Documentação):
python api/manage.py test vendedores clientes -v 2
```

---

## 👥 Integrantes do Grupo

<table align="center">
  <tr>
    <td align="center" width="33.33%">
      <a href="https://github.com/Hefestos27">
        <img src="https://github.com/Hefestos27.png" width="110" height="110" alt="Avatar de Hefestos27"><br>
        <strong>Hefestos27</strong>
      </a><br>
      <sub>Scrum Master</sub>
    </td>
    <td align="center" width="33.33%">
      <a href="https://github.com/alderiana">
        <img src="https://github.com/alderiana.png" width="110" height="110" alt="Avatar de alderiana"><br>
        <strong>alderiana</strong>
      </a><br>
      <sub>Desenvolvedora</sub>
    </td>
    <td align="center" width="33.33%">
      <a href="https://github.com/dudsstar16">
        <img src="https://github.com/dudsstar16.png" width="110" height="110" alt="Avatar de Eduarda Reis"><br>
        <strong>Eduarda Reis</strong>
      </a><br>
      <sub>Desenvolvedora</sub>
    </td>
  </tr>
</table>

---

## 👥 Guia para a Equipe

1. **Guia Rápido dos Integrantes:**
   - Leia o arquivo [`COMECE_POR_AQUI.md`](COMECE_POR_AQUI.md) para entender os objetivos, o porquê do ambiente virtual e as regras do projeto.
2. **O que é a Memória Local:**
   - Existe uma pasta de apoio local chamada `memoria/` (ignorada no Git para não poluir a entrega) que funciona como caderno de estudos. O líder pode disponibilizá-la aos membros no WhatsApp/Drive.
3. **Branches de Trabalho:**
   - Nunca trabalhe diretamente na branch `main`.
   - Crie uma branch para cada funcionalidade (ex: `feature/etl-limpeza`, `feature/api-clientes`).
4. **Dúvidas Técnicas:**
   - Dúvidas sobre palavras técnicas? Consulte os glossários simples no repositório antes de começar a codificar.
