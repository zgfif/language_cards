# Generated by Django 4.2.1 on 2024-12-06 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_word_stage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='word',
            old_name='correct_count',
            new_name='times_in_row',
        ),
    ]