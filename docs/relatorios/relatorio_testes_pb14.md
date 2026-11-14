# Relatório de Execução de Testes — PB14

**Projeto:** Primora — Distribuidora Vetor  
**Módulo:** Vendedores  
**Data da execução:** 13/11/2026

## 1. Objetivo

Registrar os resultados dos testes automatizados realizados no aplicativo Vendedores, desenvolvido com Django REST Framework.

## 2. Comando executado

```powershell
python api/manage.py test vendedores
```

## 3. Cenários testados

1. Listagem de vendedores sem autenticação.
2. Cadastro de vendedor com autenticação.
3. Consulta de vendedor por ID.
4. Atualização de vendedor com autenticação, incluindo verificação da persistência no banco.
5. Exclusão de vendedor com autenticação.
6. Bloqueio de cadastro por visitante não autenticado.
7. Bloqueio de atualização por visitante não autenticado.
8. Bloqueio de exclusão por visitante não autenticado.

## 4. Resultado

| Verificação | Resultado |
|---|---:|
| Testes encontrados | 8 |
| Testes aprovados | 8 |
| Testes reprovados | 0 |
| Duração | 15,697 segundos |
| Verificação do Django | Sem problemas |

**Status: APROVADO**

## 5. Conclusão

Os oito testes automatizados do aplicativo Vendedores foram executados com sucesso.

A execução confirmou o funcionamento dos cenários testados, incluindo as operações de CRUD, a persistência da atualização e as restrições de acesso para visitantes não autenticados.

O Django também realizou a verificação do sistema sem identificar problemas.

**Observação:** a aprovação dos testes não substitui a validação integrada dos módulos Clientes e Vendedores nem a conferência das migrações antes da integração à branch principal.

