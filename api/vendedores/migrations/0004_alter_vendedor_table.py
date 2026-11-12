# Generated manually to link Vendedor model to ETL table `vendedor`

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendedores', '0003_alter_vendedor_options_alter_vendedor_id_vendedor'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='vendedor',
            table='vendedor',
        ),
    ]

