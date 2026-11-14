from django.contrib import admin
from .models import Cliente, AuditoriaEtl


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'id_cliente',
        'razao_social',
        'cnpj_normalizado',
        'telefone_normalizado',
        'bairro_normalizado',
        'cep_normalizado',
        'vendedor',
    )
    list_filter = ('bairro_normalizado', 'vendedor')
    search_fields = ('id_cliente', 'razao_social', 'cnpj_normalizado', 'email')


@admin.register(AuditoriaEtl)
class AuditoriaEtlAdmin(admin.ModelAdmin):
    """
    Visível apenas no painel administrativo (não exposta na API pública).
    """
    list_display = (
        'id_auditoria',
        'cliente',
        'campo_afetado',
        'valor_original',
        'valor_tratado',
        'regra_aplicada',
        'data_processamento',
    )
    list_filter = ('campo_afetado', 'regra_aplicada')
    search_fields = ('cliente__id_cliente', 'valor_original', 'valor_tratado', 'regra_aplicada')
    readonly_fields = (
        'id_auditoria',
        'cliente',
        'campo_afetado',
        'valor_original',
        'valor_tratado',
        'regra_aplicada',
        'data_processamento',
    )
