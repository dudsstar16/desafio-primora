# 🛡️ Regras de Negócio e Guardrails do ETL — Distribuidora Vetor

> **O que são Guardrails?**  
> São "grades de proteção". Regras rígidas que o nosso programa em Python é obrigado a seguir para nunca estragar um dado nem inventar informação falsa.

---

## 1. Guardrail Geográfico: Conflito entre CEP e Bairro
- **O Problema:** O vendedor digitou um bairro (ex: `Sul (Aguas Claras)`), mas o serviço de consulta retornou outro bairro para o CEP cadastrado (`72140-010`).
- **A Regra (Quem Vence):** **O bairro retornado pelo ViaCEP ou pela BrasilAPI vence o texto digitado.**
- **O que o ETL faz:**
  1. Consulta o CEP no ViaCEP ou na BrasilAPI (ou usa o cache local já preenchido).
  2. Se o CEP for encontrado, o bairro retornado pelo serviço substitui o bairro digitado.
  3. **Obrigatório:** Registra um alerta na tabela de **Auditoria** com o motivo: `CONFLITO_CEP_BAIRRO_CORRIGIDO_POR_CEP_OFICIAL`.
- **E se o CEP for inválido (`00000-000`) ou estiver vazio?**
  1. O CEP inválido é descartado (vira `NULL` / vazio).
  2. Usamos o texto do `bairro_informado` limpo pelo nosso Dicionário de Bairros.
  3. Registramos na **Auditoria** que o CEP era inválido/ausente e que o bairro foi mantido pelo texto.

---

## 2. Padronização de Bairros (Agrupamento Essencial)
- **O Problema:** Subdivisões informais (`Norte`, `Sul`, `Guará I`, `Guará II`) e abreviações (`V. Pires`, `Vte Pires`) espalham os clientes em 20 linhas diferentes nos relatórios.
- **A Regra:** Tudo deve convergir para **nomes canônicos (oficiais e agrupados)**.
- **Os 4 Bairros Oficiais da Base:**
  1. `Águas Claras` *(inclui Águas Claras Norte, Sul, etc.)*
  2. `Taguatinga` *(inclui Taguatinga Sul, Taguatinga Norte, etc.)*
  3. `Vicente Pires` *(inclui V. Pires, Vte Pires, Setor Habitacional Vicente Pires)*
  4. `Guará` *(inclui Guará I, Guará II, guara - df)*
- **Exceção (Sem Dados):**
  - Se o cliente não tiver CEP **e** não tiver bairro digitado (caso do `CLI0047`), o bairro recebe `Não Informado`.

---

## 3. Regra de Ouro para Números: CNPJ, Telefone e CEP como TEXTO (`VARCHAR`)
- **O Problema:** Se salvarmos CNPJ, Telefone ou CEP como número inteiro (`INT`/`FLOAT`), o banco ou o Excel apaga os zeros à esquerda (ex: `04711671902294` perderia o `0` inicial) ou arredonda números grandes.
- **A Regra:** Todos os códigos identificadores são salvos como **TEXTO (`VARCHAR` / `str`)**, contendo **apenas dígitos** (no caso de CNPJ e Telefone):
  - **CNPJ (`cnpj_normalizado`):** Texto de exatos **14 dígitos**, sem pontos, barra ou traço.
    - *Exemplo:* `"04.711.671/9022-94"` ➔ `"04711671902294"` (preserva o zero!).
  - **Telefone (`telefone_normalizado`):** Texto com **DDD + Número** (10 dígitos para fixo, 11 dígitos para celular), removendo o código do país (`+55`), espaços, parênteses e traços.
    - *Exemplo Celular:* `"+55 61 97085-5700"` ➔ `"61970855700"`.
    - *Exemplo Fixo:* `"(61) 3491-1634"` ➔ `"6134911634"`.
  - **CEP (`cep_normalizado`):** Texto de **8 dígitos** (`"71926750"`), ou vazio/`NULL` quando ausente ou inválido (`00000-000`).

---

## 4. Padronização de Datas (`data_cadastro_normalizado`)
- **O Problema:** Datas em inglês (`Dec 24, 2023`, `jul 21, 2022`), brasileiras com barra (`28/02/2022`) ou com traço (`08-01-2022`).
- **A Regra:** Converter todas para o padrão universal de banco de dados **ISO 8601 (`AAAA-MM-DD`)**.
  - *Exemplo:* `"Dec 24, 2023"` ➔ `"2023-12-24"`.
  - *Exemplo:* `"28/02/2022"` ➔ `"2022-02-28"`.

---

## 5. Rastreabilidade Total (Auditoria)
- **A Regra:** Nenhuma transformação acontece "escondida".
- Sempre que um valor original for alterado (seja limpeza de máscara, tradução de data, padronização de bairro ou correção por conflito de CEP), uma linha é gravada na tabela de **Auditoria** explicando:
  - Quem era o cliente (`id_cliente`).
  - Qual campo mudou (`campo`).
  - Como estava antes (`valor_original`).
  - Como ficou depois (`valor_tratado`).
  - Qual regra/guardrail foi aplicada (`motivo_regra`).

