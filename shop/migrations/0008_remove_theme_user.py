# Generated by Django 4.1.3 on 2024-04-21 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_theme_selected_theme_user_usertheme'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theme',
            name='user',
        ),
    ]
