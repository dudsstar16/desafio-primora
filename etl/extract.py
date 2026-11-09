"""
Etapa 2 do ETL: Extração (Extract)
Lê o arquivo CSV bruto garantindo que TODOS os campos sejam carregados
como TEXTO (string) para nunca perder zeros à esquerda ou à direita.
"""
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_RAW_CSV = BASE_DIR / "data" / "raw" / "02-clientes_distribuidora_vetor.csv"


def extract_raw_clients(csv_path: Path | str = DEFAULT_RAW_CSV) -> list[dict[str, str]]:
    """
    Lê o CSV separado por ponto e vírgula (;) e devolve uma lista de dicionários.
    Todos os valores vêm como texto puro (str), sem conversão numérica automática.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo bruto não encontrado: {path}")

    records: list[dict[str, str]] = []
    with path.open(mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            clean_row = {
                str(k).strip(): (str(v).strip() if v is not None else "")
                for k, v in row.items()
            }
            records.append(clean_row)

    return records

