from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendedores', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendedor',
            old_name='id',
            new_name='id_vendedor',
        ),
    ]


