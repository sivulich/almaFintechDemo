# Generated by Django 3.1.4 on 2020-12-17 23:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transfer',
            old_name='destination_balance',
            new_name='balance',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='origin_balance',
        ),
    ]
