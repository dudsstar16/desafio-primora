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