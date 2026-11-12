
from django.db import models


class Vendedor(models.Model):
    id_vendedor = models.BigAutoField(primary_key=True)
    nome_vendedor = models.CharField(max_length=100)

    class Meta:
        db_table = "vendedor"
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        managed = True

    def __str__(self):
        return self.nome_vendedor
