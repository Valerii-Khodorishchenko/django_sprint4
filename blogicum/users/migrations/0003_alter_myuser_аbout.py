# Generated by Django 3.2.16 on 2024-06-15 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20240615_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='аbout',
            field=models.TextField(blank=True, max_length=256, verbose_name='О пользователе'),
        ),
    ]
