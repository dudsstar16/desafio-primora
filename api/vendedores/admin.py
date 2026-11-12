
from django.contrib import admin
from .models import Vendedor


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ("id_vendedor", "nome_vendedor")
    search_fields = ("nome_vendedor",)

