# Generated manually to register AuditoriaEtl model for Django Admin

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cliente',
            options={'managed': True, 'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes'},
        ),
        migrations.CreateModel(
            name='AuditoriaEtl',
            fields=[
                ('id_auditoria', models.BigAutoField(primary_key=True, serialize=False)),
                ('campo_afetado', models.CharField(max_length=50)),
                ('valor_original', models.TextField(blank=True, null=True)),
                ('valor_tratado', models.TextField(blank=True, null=True)),
                ('regra_aplicada', models.CharField(max_length=150)),
                ('data_processamento', models.DateTimeField()),
                ('cliente', models.ForeignKey(db_column='id_cliente', on_delete=django.db.models.deletion.DO_NOTHING, related_name='logs_auditoria', to='clientes.cliente')),
            ],
            options={
                'db_table': 'auditoria_etl',
                'managed': True,
                'verbose_name': 'Auditoria do ETL',
                'verbose_name_plural': 'Auditorias do ETL',
            },
        ),
    ]
