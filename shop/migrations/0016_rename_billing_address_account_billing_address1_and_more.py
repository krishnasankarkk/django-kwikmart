# Generated by Django 4.1.3 on 2024-04-26 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_account'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='billing_address',
            new_name='billing_address1',
        ),
        migrations.AddField(
            model_name='account',
            name='billing_address2',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='billing_address3',
            field=models.TextField(blank=True, null=True),
        ),
    ]
