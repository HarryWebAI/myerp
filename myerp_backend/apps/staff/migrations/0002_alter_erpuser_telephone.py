# Generated by Django 5.1.6 on 2025-03-16 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='erpuser',
            name='telephone',
            field=models.CharField(max_length=11, unique=True),
        ),
    ]
