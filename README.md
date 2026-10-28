# Desafio Técnico — Distribuidora Vetor (Primora)

Projeto integrado de Engenharia e Backend desenvolvido como parte do Desafio Primora.  
O objetivo é tratar dados cadastrais inconsistentes de clientes (ETL em Python), armazená-los em banco relacional (PostgreSQL) e disponibilizá-los através de uma API REST (Django REST Framework).

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
│   └── processed/          # Arquivos de dados após tratamento (futuro)
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
| `data/processed` | Dados tratados exportados no futuro |
| `etl` | Pipeline em Python (Extração, Limpeza e Carga) *(desenvolvimento futuro)* |
| `api` | Projeto Django e endpoints da API REST *(desenvolvimento futuro)* |
| `tests` | Testes automatizados de normalização *(desenvolvimento futuro)* |
| `scripts` | Scripts SQL e ferramentas de apoio *(desenvolvimento futuro)* |

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

### Etapas Futuras (Próximos Passos)
- [ ] **Etapa 2:** Modelagem do banco (MER/DER) e planejamento da tabela de auditoria.
- [ ] **Etapa 3:** Desenvolvimento do pipeline ETL em Python (normalização de bairros, CEPs via ViaCEP/BrasilAPI, CNPJ, telefone e datas).
- [ ] **Etapa 4:** Testes unitários automatizados da limpeza de dados com chamadas simuladas (*mocks*).
- [ ] **Etapa 5:** Criação do projeto Django, models, migrações e carga dos dados no PostgreSQL.
- [ ] **Etapa 6:** Implementação das rotas da API REST (CRUD, filtros por bairro/vendedor e autenticação).
- [ ] **Etapa 7:** Documentação interativa da API com `drf-spectacular` (Redoc/Swagger) e relatório final.

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

## 👥 Guia para a Equipe

1. **Memória Local do Projeto:**
   - Existe uma pasta local de apoio chamada `memoria/` (ignorada no Git) para guiar os estudos e o passo a passo com explicações simples para quem está começando.
2. **Branches de Trabalho:**
   - Nunca trabalhe diretamente na branch `main`.
   - Crie uma branch para cada funcionalidade (ex: `feature/etl-limpeza`, `feature/api-clientes`).
3. **Dúvidas Técnicas:**
   - Consulte o glossário e guias na memória local do projeto antes de iniciar novas etapas.
