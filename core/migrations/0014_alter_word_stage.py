# Generated by Django 4.2.1 on 2024-12-06 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_remove_word_reset_date_word_correct_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='stage',
            field=models.CharField(default='day', max_length=100),
        ),
    ]
