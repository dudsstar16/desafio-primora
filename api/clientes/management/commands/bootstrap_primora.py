import csv
import os
from datetime import datetime
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction
from django.utils import timezone

from clientes.models import AuditoriaEtl, Cliente
from vendedores.models import Vendedor

DEMO_ADMIN_USERS = ('duda', 'bruno', 'ana')


class Command(BaseCommand):
    help = 'Carrega os CSVs processados e garante as contas administrativas do protótipo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Não altera as tabelas de negócio se já tiverem dados, mas garante os usuários do protótipo.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        user_count = self._ensure_demo_admins()
        if options['if_empty'] and (
            Vendedor.objects.exists() or Cliente.objects.exists() or AuditoriaEtl.objects.exists()
        ):
            self.stdout.write(self.style.WARNING(
                f'Carga ignorada: banco já possui dados ({user_count} contas verificadas).'
            ))
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
            f'Carga concluída: {seller_count} vendedores, {client_count} clientes, '
            f'{audit_count} auditorias e {user_count} contas administrativas.'
        ))

    @staticmethod
    def _ensure_demo_admins():
        user_model = get_user_model()
        password = os.getenv('DEMO_ADMIN_PASSWORD', '123456')
        for username in DEMO_ADMIN_USERS:
            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@primora.local',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                },
            )
            updated = False
            if not user.is_staff or not user.is_superuser or not user.is_active:
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                updated = True
            if created or not user.has_usable_password():
                user.set_password(password)
                updated = True
            if updated:
                user.save()
        return len(DEMO_ADMIN_USERS)

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
