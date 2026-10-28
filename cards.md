# 🗂️ Cards de Boas-Vindas e Alinhamento da Equipe

Este documento foi criado no formato de **Cards Rápidos** para ajudar todos os integrantes do grupo a entenderem o projeto rapidamente, sem enrolação e em frases curtas.

---

### 💳 Card 1: O que é o Nosso Projeto?
- **Cliente Fictício:** Distribuidora Vetor (atacadista de mercadorias no DF).
- **O Problema:** Os dados de 47 clientes foram cadastrados de qualquer jeito (bairros escritos de formas diferentes, CEPs errados, telefones sem padrão).
- **A Nossa Missão:**  
  1. Limpar e padronizar esses dados usando Python (**ETL**).  
  2. Guardar a base tratada em um banco de dados (**PostgreSQL**).  
  3. Criar uma **API** em **Django** para que outros sistemas possam consultar esses clientes pela internet.

---

### 💳 Card 2: Status do Checklist (Etapa 1 — Concluída!)
- [x] **Repositório privado criado:** Sim, já está no ar.
- [x] **README e .gitignore configurados:** Sim, tudo protegido e organizado.
- [x] **Pastas principais criadas:** Sim (`docs`, `data`, `etl`, `api`, `tests`, `scripts`).
- [x] **PDFs com as regras:** Salvos em `docs/requisitos/`.
- [x] **CSV com os 47 clientes originais:** Salvo em `data/raw/02-clientes_distribuidora_vetor.csv`.
- [x] **Convites para a equipe:** Convites enviados no GitHub aos integrantes!

---

### 💳 Card 3: Por que Ativar o Ambiente Virtual (`venv`)?
- **O que é o `venv`:** É uma bolha de proteção no seu computador.
- **Para que serve:** Garante que todos nós usamos as mesmas versões das bibliotecas (como Django e Pandas), sem misturar com outros programas do seu Windows.
- **Por que TEM que ativar:** Criar a pasta do ambiente não adianta nada se você não ligar a chavinha. **Ativar** avisa ao terminal: *"Use as ferramentas de dentro desta pasta!"*.
- **Como ativar no Windows:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Se aparecer `(venv)` verdinho no início da linha, está pronto!)*

---

### 💳 Card 4: Divisão do Trabalho (2 Fases)
1. **Fase 1 — Engenharia de Dados (ETL):**
   - Ler o arquivo CSV original.
   - Corrigir a grafia dos bairros (ex: transformar "aguas claras" em "Águas Claras").
   - Buscar CEPs em APIs públicas gratuitas (ViaCEP).
   - Anotar em uma tabela de **auditoria** tudo o que foi alterado.
   - Salvar tudo no banco de dados PostgreSQL.

2. **Fase 2 — Desenvolvimento Web Backend (API REST):**
   - Criar um sistema em Django.
   - Criar rotas web para listar clientes, buscar por bairro e buscar por vendedor.
   - Criar login com Token de segurança.
   - Criar a página de documentação interativa (Redoc).

---

### 💳 Card 5: Como Trabalhar em Equipe com o Git?
- **Regra de ouro:** Nunca programe direto na branch `main`.
- **Rotina de trabalho:**
  1. Antes de começar o dia: `git pull origin main` (puxar o que os colegas fizeram).
  2. Criar sua branch: `git checkout -b feature/minha-tarefa`.
  3. Salvar o progresso: `git commit -m "Explicação curta do que fiz"`.
  4. Enviar para o GitHub: `git push -u origin feature/minha-tarefa`.
  5. Avisar o grupo no WhatsApp para aprovar o Pull Request!

---

### 💳 Card 6: Onde Encontrar Ajuda e Dúvidas?
- A pasta local [`memoria/`](file:///c:/Users/alunocceia/desafio-primora/memoria) contém guias completos:
  - Dicionário de termos técnicos descomplicados.
  - Passo a passo de cada uma das 7 fases.
  - Explicação completa de como o Python gerencia o ambiente virtual.
