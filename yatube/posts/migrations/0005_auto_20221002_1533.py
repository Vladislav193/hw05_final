# Generated by Django 2.2.6 on 2022-10-02 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20221001_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Задача', max_length=200, unique=True, verbose_name='Заголовок'),
        ),
    ]