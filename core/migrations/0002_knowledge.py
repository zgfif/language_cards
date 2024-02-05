# Generated by Django 4.2.1 on 2023-10-30 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Knowledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('en_ru', models.BooleanField(default=False)),
                ('ru_en', models.BooleanField(default=False)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.word')),
            ],
        ),
    ]