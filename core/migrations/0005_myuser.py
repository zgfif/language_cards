# Generated by Django 4.2.1 on 2024-01-01 09:13

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0004_word_en_ru_word_ru_en_delete_knowledge'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
