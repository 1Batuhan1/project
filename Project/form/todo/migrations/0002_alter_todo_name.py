# Generated by Django 4.2.13 on 2024-07-05 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='name',
            field=models.CharField(max_length=500, verbose_name='name'),
        ),
    ]
