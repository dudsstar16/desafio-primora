from django.db import models


class Cliente(models.Model):
    id_cliente = models.CharField(max_length=20, primary_key=True)
    razao_social = models.CharField(max_length=150)
    cnpj_normalizado = models.CharField(max_length=14)
    telefone_normalizado = models.CharField(max_length=11)
    email = models.CharField(max_length=150)
    bairro_normalizado = models.CharField(max_length=100)
    cep_normalizado = models.CharField(max_length=8, null=True, blank=True)
    cidade = models.CharField(max_length=50)
    uf = models.CharField(max_length=2)
    data_cadastro_normalizado = models.DateField()
    vendedor = models.ForeignKey(
    'vendedores.Vendedor',
    on_delete=models.DO_NOTHING,
    db_column='vendedor_id',
    related_name='clientes'
)

    class Meta:
        db_table = 'cliente'
        managed = True
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.id_cliente} - {self.razao_social}"


class AuditoriaEtl(models.Model):
    """
    Tabela de Auditoria do ETL.
    Regra oficial do desafio: permanece registrada apenas no Django Admin,
    não sendo exposta em nenhuma rota pública da API.
    """
    id_auditoria = models.BigAutoField(primary_key=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.DO_NOTHING,
        db_column='id_cliente',
        related_name='logs_auditoria',
    )
    campo_afetado = models.CharField(max_length=50)
    valor_original = models.TextField(null=True, blank=True)
    valor_tratado = models.TextField(null=True, blank=True)
    regra_aplicada = models.CharField(max_length=150)
    data_processamento = models.DateTimeField()

    class Meta:
        db_table = 'auditoria_etl'
        managed = True
        verbose_name = 'Auditoria do ETL'
        verbose_name_plural = 'Auditorias do ETL'

    def __str__(self):
        return f"[{self.cliente_id}] {self.campo_afetado}: {self.regra_aplicada}"
