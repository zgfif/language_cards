# Generated by Django 4.2.1 on 2023-10-30 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_knowledge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledge',
            name='word',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.word'),
        ),
    ]