"""
Etapa 4C do ETL: Registro de Auditoria (Audit Log)
Guarda o histórico de todas as correções feitas linha por linha, campo por campo.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class AuditEntry:
    id_cliente: str
    campo_afetado: str
    valor_original: str
    valor_tratado: str
    regra_aplicada: str
    data_processamento: str


class AuditLogger:
    """
    Acumula os registros de auditoria durante a execução do pipeline ETL.
    """

    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def log_change(
        self,
        id_cliente: str,
        campo_afetado: str,
        valor_original: str | None,
        valor_tratado: str | None,
        regra_aplicada: str | None,
    ) -> None:
        if not regra_aplicada:
            return
        orig_str = str(valor_original) if valor_original is not None else ""
        trat_str = str(valor_tratado) if valor_tratado is not None else "NULL"

        entry = AuditEntry(
            id_cliente=id_cliente,
            campo_afetado=campo_afetado,
            valor_original=orig_str,
            valor_tratado=trat_str,
            regra_aplicada=regra_aplicada,
            data_processamento=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.entries.append(entry)

    def to_dicts(self) -> list[dict[str, str]]:
        return [asdict(e) for e in self.entries]

