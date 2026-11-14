from django.db import models


class Vendedor(models.Model):
    id_vendedor = models.AutoField(primary_key=True)
    nome_vendedor = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = True
        db_table = "vendedor"
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"

    def __str__(self):
        return self.nome_vendedor