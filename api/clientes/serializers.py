from rest_framework import serializers
from .models import Cliente
from vendedores.models import Vendedor


class ClienteSerializer(serializers.ModelSerializer):

    vendedor_id = serializers.PrimaryKeyRelatedField(
        source='vendedor',
        queryset=Vendedor.objects.all()
    )

    class Meta:
        model = Cliente
        fields = [
            'id_cliente',
            'razao_social',
            'cnpj_normalizado',
            'telefone_normalizado',
            'email',
            'bairro_normalizado',
            'cep_normalizado',
            'cidade',
            'uf',
            'data_cadastro_normalizado',
            'vendedor_id',
        ]