# 🚀 Comece Por Aqui — Guia Inicial da Equipe

Seja muito bem-vindo ao projeto do **Desafio Primora**!  
Este guia foi feito para você entender tudo rápido, sem palavras difíceis e em frases curtas.

---

## 🧠 1. O que é a "Memória Local"?

Você deve ter ouvido falar da **memória local** do projeto.  
Aqui está a explicação do que ela é:

- **O que significa a palavra "Local":**  
  Significa que o arquivo está **apenas no computador de quem criou**.  
  Ele **não** foi enviado para a internet (GitHub).

- **O que é essa memória:**  
  É o nosso **caderno de estudos e anotações internas**.  
  Lá nós guardamos:
  - O resumo dos slides da aula.
  - As regras oficiais do desafio.
  - Um dicionário explicando cada palavra técnica em português simples.
  - O roteiro detalhado do que fazer em cada etapa.

- **Por que ela NÃO vai para o GitHub?**  
  No arquivo `.gitignore`, colocamos a regra para não enviar a pasta `memoria/`.  
  Fizemos isso de propósito para manter o repositório oficial limpo e profissional para quem for avaliar o projeto.

- **Como você pode acessar esse caderno de estudos?**  
  Os arquivos deste guia aqui (`COMECE_POR_AQUI.md`) já trazem os pontos principais!  
  Além disso, o criador do projeto pode enviar a pastinha `memoria` compactada no grupo do WhatsApp ou Google Drive para quem quiser ler todos os detalhes no próprio computador.

---

## 🎯 2. Qual é o Objetivo do Nosso Projeto?

- **A empresa fictícia:** Chama-se Distribuidora Vetor.
- **O problema dela:** Ao longo de anos, os vendedores cadastraram 47 clientes no sistema de qualquer jeito.
  - Bairros com nomes diferentes (ex: "Águas Claras", "aguas claras", "AGUAS CLARAS").
  - Telefones e CNPJs em formatos misturados.
  - CEPs errados ou em branco.
- **O que nós vamos construir:**
  1. **Parte 1 (ETL em Python):** Um programa em Python para limpar e padronizar todos os dados e salvar no banco de dados **PostgreSQL**.
  2. **Parte 2 (API em Django):** Um sistema web para que qualquer pessoa possa consultar esses clientes pela internet de forma rápida e segura.

---

## 🧪 3. Por que precisamos do Ambiente Virtual (`venv`)?

- **O que é o `venv`:**  
  É uma **caixa isolada** criada no seu computador só para este projeto.

- **Para que serve:**  
  Evita que os pacotes deste trabalho se misturem com outros programas do seu computador.  
  Garante que o código funcione **exatamente igual** no computador dos três integrantes.

- **Por que TEMOS que ATIVAR?**  
  Criar a pasta não é o suficiente.  
  **Ativar** é apertar o botão que avisa ao terminal:  
  *"Atenção: use os programas de dentro da caixinha `venv`, e não os do Windows geral!"*

- **Como ativar no Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  > **Dica de ouro:** Se der erro de script bloqueado no Windows, rode este comando antes:  
  > `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

- **Como saber se deu certo:**  
  Aparece a palavra `(venv)` bem no comecinho da sua linha de comando.

---

## 🗂️ 4. O que significa cada pasta do projeto?

| Pasta | O que vai dentro? |
| :--- | :--- |
| `data/raw/` | O arquivo original `02-clientes_distribuidora_vetor.csv` (intocado). |
| `data/processed/` | Onde salvaremos os dados depois de tratados. |
| `docs/requisitos/` | Os PDFs oficiais com todas as regras do desafio. |
| `docs/arquitetura/` | Planejamento técnico e desenhos de como tudo se conecta. |
| `docs/modelagem/` | Desenho das tabelas do banco de dados (MER e DER). |
| `docs/relatorios/` | Relatório final explicando as decisões que tomamos. |
| `etl/` | Nossos códigos em Python que limpam os dados *(passo futuro)*. |
| `api/` | Nosso sistema web em Django com as rotas *(passo futuro)*. |
| `tests/` | Testes automáticos para garantir que a limpeza não errou *(passo futuro)*. |
| `scripts/` | Comandos extras em SQL e utilitários *(passo futuro)*. |

---

## 🐙 5. Regras de Convivência no Git

Para ninguém apagar o trabalho do colega sem querer:

1. **Nunca programe na branch `main`:**  
   A branch `main` é sagrada. Ela só recebe código testado e aprovado.
2. **Crie uma branch para a sua tarefa:**  
   Exemplo: `git checkout -b feature/nome-da-sua-tarefa`.
3. **Antes de começar o dia:**  
   Rode `git pull origin main` para baixar as novidades que seus colegas enviaram.
4. **Quando terminar sua parte:**  
   Envie sua branch com `git push` e abra um **Pull Request** no GitHub para o grupo revisar junto.

---

## 💬 6. Resumo Rápido de Dúvidas

- **Pergunta:** O que eu devo fazer agora no meu computador?  
  **Resposta:** Clone o repositório, crie seu `venv`, ative o `venv` e instale as dependências (`pip install -r requirements.txt`).
- **Pergunta:** Já posso começar a escrever o código do Django ou da API?  
  **Resposta:** Ainda não! Nosso próximo passo em grupo é a **Modelagem do Banco de Dados** (desenhar as tabelas).
