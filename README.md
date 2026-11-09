# Desafio Técnico — Distribuidora Vetor (Primora)

Projeto integrado de Engenharia e Backend desenvolvido como parte do Desafio Primora.  
O objetivo é tratar dados cadastrais inconsistentes de clientes (ETL em Python), armazená-los em banco relacional (PostgreSQL) e disponibilizá-los através de uma API REST (Django REST Framework).

> 👉 **Primeira vez no repositório?**  
> Leia nosso guia super simples e direto para o grupo: **[COMECE_POR_AQUI.md](COMECE_POR_AQUI.md)**.

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
| `api` | Projeto Django e endpoints da API REST *(desenvolvimento futuro)* |
| `tests` | Testes automatizados das regras de limpeza e dos conflitos de CEP |
| `scripts` | Script pronto para carregar as tabelas no PostgreSQL |

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

### Parte 2 — Próximos Passos
- [ ] Criar o projeto Django, os models e as migrações.
- [ ] Implementar CRUD, filtros e autenticação da API.
- [ ] Registrar a auditoria somente no Django Admin.
- [ ] Publicar a documentação OpenAPI, Redoc e Swagger.

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
