"""
Etapa 4B do ETL: Padronização de Bairros e Guardrail de Conflito (CEP x Bairro)
Une todas as variações nos 4 bairros principais ('Águas Claras', 'Taguatinga',
'Vicente Pires', 'Guará') e faz o bairro retornado pelo serviço de CEP prevalecer
em caso de conflito com o texto digitado.
"""
import re
import unicodedata
from etl.cep_service import CepService

# Dicionário de correspondência determinístico (chave limpa sem acento -> Nome Canônico Oficial)
CANONICAL_NEIGHBORHOOD_MAP: dict[str, str] = {
    # Grupo 1: Águas Claras
    "aguas claras": "Águas Claras",
    "sul aguas claras": "Águas Claras",
    "norte aguas claras": "Águas Claras",
    "aguas claras sul": "Águas Claras",
    "aguas claras norte": "Águas Claras",
    # Grupo 2: Taguatinga
    "taguatinga": "Taguatinga",
    "taguatinga sul": "Taguatinga",
    "taguatinga norte": "Taguatinga",
    "taguatinga norte taguatinga": "Taguatinga",
    "taguatinga sul taguatinga": "Taguatinga",
    "taguatinga centro": "Taguatinga",
    # Grupo 3: Vicente Pires
    "vicente pires": "Vicente Pires",
    "v pires": "Vicente Pires",
    "vte pires": "Vicente Pires",
    "setor habitacional vicente pires": "Vicente Pires",
    "shvp": "Vicente Pires",
    # Grupo 4: Guará
    "guara": "Guará",
    "guara i": "Guará",
    "guara ii": "Guará",
    "guara 1": "Guará",
    "guara 2": "Guará",
}


def clean_text_key(raw_text: str) -> str:
    """
    Transforma qualquer texto sujo numa chave limpa para busca no dicionário:
    1. Passa para minúsculas
    2. Remove acentos ('Á' -> 'a')
    3. Remove sufixos '/df' ou '- df'
    4. Troca parênteses, pontos e traços por espaço
    """
    if not raw_text:
        return ""
    # Remove acentos
    norm = unicodedata.normalize("NFKD", raw_text)
    no_accents = "".join(c for c in norm if not unicodedata.combining(c))
    lowered = no_accents.lower().strip()

    # Remove sufixo de UF no final (ex: '- df', '/df')
    lowered = re.sub(r"[\s/\-]+df$", "", lowered)

    # Mantém apenas letras e números separados por 1 espaço
    cleaned = re.sub(r"[^a-z0-9]+", " ", lowered).strip()
    return cleaned


def canonicalize_neighborhood_name(raw_name: str) -> str | None:
    """
    Recebe um nome de bairro (digitado pelo cliente ou vindo da API de CEP)
    e devolve um dos 4 nomes oficiais padronizados.
    """
    key = clean_text_key(raw_name)
    if not key:
        return None

    # 1. Busca direta no dicionário de variações
    if key in CANONICAL_NEIGHBORHOOD_MAP:
        return CANONICAL_NEIGHBORHOOD_MAP[key]

    # 2. Busca por palavra-chave de segurança
    if "aguas claras" in key:
        return "Águas Claras"
    if "taguatinga" in key:
        return "Taguatinga"
    if "pires" in key:
        return "Vicente Pires"
    if "guara" in key:
        return "Guará"

    return raw_name.strip()


def resolve_address(
    raw_bairro: str,
    raw_cep: str,
    cep_service: CepService,
) -> dict[str, str | None]:
    """
    Aplica as regras de negócio e o GUARDRAIL de conflito entre CEP e Bairro.
    Retorna um dicionário com:
      - cep_normalizado: texto 8 dígitos ou None
      - regra_cep: motivo para a auditoria de CEP (se houve mudança/erro)
      - bairro_normalizado: nome oficial final
      - regra_bairro: motivo para a auditoria de Bairro (ex: conflito corrigido pelo CEP)
    """
    cep_digits, cep_rule = cep_service.clean_cep_digits(raw_cep)
    bairro_from_text = canonicalize_neighborhood_name(raw_bairro)

    bairro_from_cep = None
    if cep_digits:
        cep_info = cep_service.lookup_cep(cep_digits)
        if cep_info and cep_info.get("valido"):
            bairro_from_cep = canonicalize_neighborhood_name(cep_info.get("bairro_api", ""))
        else:
            # CEP tinha 8 dígitos mas não existe nos Correios
            cep_digits = None
            cep_rule = "CEP_NAO_ENCONTRADO_NA_API_DESCARTADO"

    # --- GUARDRAIL DE DECISÃO DO BAIRRO ---
    # Caso 1: Temos um CEP encontrado no ViaCEP ou na BrasilAPI
    if bairro_from_cep:
        final_bairro = bairro_from_cep
        if bairro_from_text and bairro_from_text != bairro_from_cep:
            # Conflito! O texto dizia um bairro (ex: Águas Claras), mas o CEP é de outro (ex: Taguatinga)
            bairro_rule = (
                f"GUARDRAIL_CONFLITO_CEP_VENCEU_TEXTO "
                f"(Texto sugeria '{bairro_from_text}', mas CEP {cep_digits} pertence a '{bairro_from_cep}')"
            )
        elif (raw_bairro or "").strip() != final_bairro:
            bairro_rule = "PADRONIZACAO_BAIRRO_CONFIRMADO_POR_CEP_OFICIAL"
        else:
            bairro_rule = None

    # Caso 2: Não temos CEP válido (vazio ou 00000-000), mas temos o texto do bairro
    elif bairro_from_text:
        final_bairro = bairro_from_text
        if (raw_bairro or "").strip() != final_bairro:
            bairro_rule = "PADRONIZACAO_TEXTO_DICIONARIO_SEM_CEP_CONFIAVEL"
        else:
            bairro_rule = None

    # Caso 3: Nem CEP nem Bairro foram informados (ex: CLI0047)
    else:
        final_bairro = "Não Informado"
        bairro_rule = "BAIRRO_E_CEP_AUSENTES_DEFINIDO_NAO_INFORMADO"

    return {
        "cep_normalizado": cep_digits,
        "regra_cep": cep_rule,
        "bairro_normalizado": final_bairro,
        "regra_bairro": bairro_rule,
    }

