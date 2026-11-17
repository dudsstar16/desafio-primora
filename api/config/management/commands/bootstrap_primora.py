import csv
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction
from django.utils import timezone

from clientes.models import AuditoriaEtl, Cliente
from vendedores.models import Vendedor


class Command(BaseCommand):
    help = 'Carrega os CSVs processados de forma idempotente no banco configurado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Não altera o banco se qualquer tabela de negócio já tiver dados.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['if_empty'] and (
            Vendedor.objects.exists() or Cliente.objects.exists() or AuditoriaEtl.objects.exists()
        ):
            self.stdout.write(self.style.WARNING('Carga ignorada: banco já possui dados.'))
            return

        project_root = Path(__file__).resolve().parents[4]
        processed = project_root / 'data' / 'processed'
        paths = {
            'sellers': processed / 'vendedores_limpos.csv',
            'clients': processed / 'clientes_limpos.csv',
            'audit': processed / 'auditoria_etl.csv',
        }
        missing = [str(path) for path in paths.values() if not path.exists()]
        if missing:
            raise CommandError(f"Arquivos processados ausentes: {', '.join(missing)}")

        seller_count = self._load_sellers(paths['sellers'])
        client_count = self._load_clients(paths['clients'])
        audit_count = self._load_audit(paths['audit'])
        self._reset_sequences()
        self.stdout.write(self.style.SUCCESS(
            f'Carga concluída: {seller_count} vendedores, {client_count} clientes e '
            f'{audit_count} auditorias.'
        ))

    @staticmethod
    def _rows(path):
        with path.open(encoding='utf-8-sig', newline='') as csv_file:
            yield from csv.DictReader(csv_file, delimiter=';')

    def _load_sellers(self, path):
        count = 0
        for row in self._rows(path):
            Vendedor.objects.update_or_create(
                id_vendedor=int(row['id_vendedor']),
                defaults={'nome_vendedor': row['nome_vendedor']},
            )
            count += 1
        return count

    @staticmethod
    def _reset_sequences():
        statements = connection.ops.sequence_reset_sql(
            no_style(), [Vendedor, Cliente, AuditoriaEtl]
        )
        if statements:
            with connection.cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)

    def _load_clients(self, path):
        count = 0
        for row in self._rows(path):
            Cliente.objects.update_or_create(
                id_cliente=row['id_cliente'],
                defaults={
                    'razao_social': row['razao_social'],
                    'cnpj_normalizado': row['cnpj_normalizado'],
                    'telefone_normalizado': row['telefone_normalizado'],
                    'email': row['email'],
                    'bairro_normalizado': row['bairro_normalizado'],
                    'cep_normalizado': row['cep_normalizado'] or None,
                    'cidade': row['cidade'],
                    'uf': row['uf'],
                    'data_cadastro_normalizado': row['data_cadastro_normalizado'],
                    'vendedor_id': int(row['vendedor_id']),
                },
            )
            count += 1
        return count

    def _load_audit(self, path):
        count = 0
        for row in self._rows(path):
            processed_at = datetime.fromisoformat(row['data_processamento'])
            if timezone.is_naive(processed_at):
                processed_at = timezone.make_aware(processed_at)
            AuditoriaEtl.objects.update_or_create(
                id_auditoria=int(row['id_auditoria']),
                defaults={
                    'cliente_id': row['id_cliente'],
                    'campo_afetado': row['campo_afetado'],
                    'valor_original': row['valor_original'] or None,
                    'valor_tratado': row['valor_tratado'] or None,
                    'regra_aplicada': row['regra_aplicada'],
                    'data_processamento': processed_at,
                },
            )
            count += 1
        return count
