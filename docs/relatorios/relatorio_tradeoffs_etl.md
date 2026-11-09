# 📄 Relatório Técnico de Decisões e Trade-offs do ETL — Distribuidora Vetor

## 1. Visão Geral da Solução
Construímos um pipeline de ETL modular em Python (`etl/`) que recebe os **47 registros brutos** da Distribuidora Vetor (`02-clientes_distribuidora_vetor.csv`), corrige inconsistências estruturais e semânticas, registra **188 eventos de auditoria** e entrega as 3 tabelas relacionais prontas (`vendedor`, `cliente` e `auditoria_etl`).

---

## 2. O que Decidimos Automatizar vs. Tratar Manualmente (Trade-offs)

| Problema Encontrado | Abordagem Escolhida | Justificativa (Trade-off) |
| :--- | :--- | :--- |
| **CNPJ e Telefone em formatos mistos** | **100% Automatizado (Texto Puro):** Remoção de pontuação e DDI `+55`, mantendo como texto (`VARCHAR`). | Salvar como texto numérico (`"04711671902294"`, `"61970855700"`) impede que o banco ou planilhas apaguem zeros à esquerda ou à direita. |
| **Datas em 3 idiomas/formatos** | **100% Automatizado:** Parser multi-formato convertendo ISO, BR (`DD/MM/AAAA`, `DD-MM-AAAA`) e Inglês (`Dec 24, 2023`) para `AAAA-MM-DD`. | Garante ordenação cronológica exata no banco SQL sem intervenção humana. |
| **20 variações de escrita de Bairros** | **Híbrido (Normalização + Dicionário Curado):** Limpeza de acentos/caixa combinada com dicionário canônico para os **4 bairros do DF**. | Em bases pequenas/médias, um dicionário determinístico tem 100% de precisão, ao contrário de algoritmos difusos (*fuzzy matching*) que poderiam confundir subdivisões. |
| **Consultas à API de CEP (ViaCEP / BrasilAPI)** | **Automatizado com Cache Local (`cep_cache.json`):** Consulta online apenas no primeiro encontro do CEP. | Evita lentidão, protege contra quedas de internet e permite rodar testes instantaneamente. |
| **Conflito entre Bairro Digitado e CEP** | **Guardrail Automático Auditado (consulta de CEP vence):** Quando o CEP é encontrado no serviço de consulta, o bairro retornado prevalece sobre o texto livre. | A resposta do serviço de CEP é mais padronizada que o texto livre, mas a correção continua registrada para revisão. |
| **Cliente sem Bairro e sem CEP (`CLI0047`)** | **Classificação como `"Não Informado"` + Alerta na Auditoria para Revisão Comercial.** | Não é possível adivinhar o endereço sem CEP e sem bairro; inventar um bairro violaria a integridade dos relatórios. |

---

## 3. Casos Críticos Resolvidos pelo Guardrail de Conflito

Durante a execução do ETL, o Guardrail identificou **3 divergências** entre o bairro digitado e o resultado dos serviços de consulta de CEP:

1. **`CLI0002` (Comercial São Judas):**
   - *Digitado:* `Sul (Aguas Claras)` | *CEP:* `72140-010`
   - *Decisão:* O serviço de consulta retornou QNM 32, em **Taguatinga**, para o CEP `72140-010`. O bairro foi corrigido para **`Taguatinga`** e registrado na auditoria.
2. **`CLI0017` (Casa de Carnes Ouro Fino) e `CLI0033` (Loja Bom Retiro):**
   - *Digitado:* `Vte Pires` / `Vicente Pires - DF` | *CEP:* `72110-800`
   - *Decisão:* O serviço de consulta retornou **Taguatinga Norte** para o CEP `72110-800`. O bairro foi corrigido para **`Taguatinga`** e registrado na auditoria.
3. **Grupo do Bairro `Guará` (6 clientes) e CEPs `00000-000` (3 clientes):**
   - *Decisão:* Os CEPs inválidos foram limpos para `NULL` e os bairros foram padronizados pelo dicionário textual (`Guará`, `Águas Claras`, `Taguatinga`), preservando a contagem regional sem inventar CEPs falsos.

---

## 4. Resultado Final da Consolidação por Bairro

Antes do ETL, um relatório agrupado por bairro gerava **21 linhas fragmentadas**. Após o ETL, os **47 clientes** ficaram perfeitamente distribuídos em:
- **Águas Claras:** 21 clientes
- **Taguatinga:** 13 clientes
- **Vicente Pires:** 6 clientes
- **Guará:** 6 clientes
- **Não Informado:** 1 cliente (`CLI0047`)

---

## 5. Limites Conhecidos da Abordagem
1. **CEPs Gerais ou de Divisa:** Em regiões administrativas do DF próximas (como Vicente Pires e Taguatinga), um cliente pode ter informado o CEP de uma agência ou rua vizinha. Por isso toda correção por CEP gera log em `auditoria_etl`.
2. **Novos Bairros Fora dos 4 Mapeados:** Se a distribuidora expandir para outras regiões (ex: *Ceilândia*, *Asa Sul*), novas variantes informais deverão ser adicionadas ao `CANONICAL_NEIGHBORHOOD_MAP`.

