# Generated by Django 5.0.4 on 2024-04-15 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attempt',
            name='response',
            field=models.BooleanField(verbose_name='Успешно'),
        ),
    ]
