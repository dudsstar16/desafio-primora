"""
Etapa 3 do ETL: Transformação de Campos Simples (CNPJ, Telefone e Data)
Garante que CNPJ e Telefone fiquem como TEXTO contendo apenas números
(preservando zeros) e converte todas as datas para o padrão ISO (AAAA-MM-DD).
"""
import re
from datetime import datetime

# Mapeamento de meses em inglês/português abreviados para número do mês
MONTH_MAP = {
    "jan": 1,
    "feb": 2, "fev": 2,
    "mar": 3,
    "apr": 4, "abr": 4,
    "may": 5, "mai": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8, "ago": 8,
    "sep": 9, "set": 9,
    "oct": 10, "out": 10,
    "nov": 11,
    "dec": 12, "dez": 12,
}


def normalize_cnpj(raw_cnpj: str) -> tuple[str, str | None]:
    """
    Remove pontos, barras, traços e espaços do CNPJ, mantendo como TEXTO (str).
    Retorna: (cnpj_limpo, regra_auditoria_ou_None)
    """
    original = (raw_cnpj or "").strip()
    digits = re.sub(r"\D", "", original)

    # Se por acaso algum sistema anterior comeu zero à esquerda, garante 14 caracteres
    if 0 < len(digits) < 14:
        digits = digits.zfill(14)

    if digits != original:
        return digits, "LIMPEZA_MASCARA_CNPJ_PARA_TEXTO_14_DIGITOS"
    return digits, None


def normalize_phone(raw_phone: str) -> tuple[str, str | None]:
    """
    Padroniza telefone como TEXTO contendo apenas DDD + número (ex: '61970855700').
    Remove o código do país (+55), parênteses, espaços e traços.
    Retorna: (telefone_limpo, regra_auditoria_ou_None)
    """
    original = (raw_phone or "").strip()
    digits = re.sub(r"\D", "", original)

    # Remove DDI 55 do Brasil se tiver 12 ou 13 dígitos começando com 55
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]

    if digits != original:
        return digits, "PADRONIZACAO_TELEFONE_TEXTO_DDD_NUMERO"
    return digits, None


def normalize_date(raw_date: str) -> tuple[str, str | None]:
    """
    Converte datas em formatos variados (ISO, BR com barra/traço, Inglês textual)
    para o formato padrão de banco de dados 'AAAA-MM-DD'.
    Retorna: (data_iso, regra_auditoria_ou_None)
    """
    original = (raw_date or "").strip()
    if not original:
        return "", "DATA_AUSENTE"

    # 1. Já está no padrão ISO (AAAA-MM-DD)?
    if re.match(r"^\d{4}-\d{2}-\d{2}$", original):
        return original, None

    # 2. Formato Brasileiro com barra (DD/MM/AAAA) ou traço (DD-MM-AAAA)
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(original, fmt)
            return dt.strftime("%Y-%m-%d"), "CONVERSAO_DATA_BR_PARA_ISO"
        except ValueError:
            pass

    # 3. Formato textual em Inglês/Português (ex: 'Dec 24, 2023', 'jul 21, 2022')
    match_text = re.match(r"^([A-Za-zçÇ]{3})[a-z]*\s+(\d{1,2}),?\s+(\d{4})$", original)
    if match_text:
        month_str, day_str, year_str = match_text.groups()
        month_num = MONTH_MAP.get(month_str.lower())
        if month_num:
            dt = datetime(int(year_str), month_num, int(day_str))
            return dt.strftime("%Y-%m-%d"), "CONVERSAO_DATA_TEXTO_INGLES_PARA_ISO"

    raise ValueError(f"Formato de data não reconhecido: {original}")

