from rest_framework import serializers
from .models import Cliente
from vendedores.models import Vendedor


def mask_suffix(value, visible):
    if len(value) <= visible:
        return '*' * len(value)
    return '*' * (len(value) - visible) + value[-visible:]


def mask_email(value):
    if not value:
        return ''
    local, _, domain = value.partition('@')
    if not local or not domain or '@' in domain:
        return '***'
    return f'{local[0]}***@{domain}'


class ClienteSerializer(serializers.ModelSerializer):
    """Nas consultas públicas, apenas os finais do CNPJ e do telefone e a inicial e o domínio do e-mail são visíveis."""

    vendedor_id = serializers.PrimaryKeyRelatedField(
        source='vendedor',
        queryset=Vendedor.objects.all()
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request is not None and request.user.is_authenticated:
            return data

        data['cnpj_normalizado'] = mask_suffix(data['cnpj_normalizado'], 2)
        data['telefone_normalizado'] = mask_suffix(data['telefone_normalizado'], 4)
        data['email'] = mask_email(data['email'])
        return data

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
