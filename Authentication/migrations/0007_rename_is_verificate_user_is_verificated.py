# Generated by Django 4.0.5 on 2022-08-19 01:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0006_alter_verification_expiration_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_verificate',
            new_name='is_verificated',
        ),
    ]