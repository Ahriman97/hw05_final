# Generated by Django 2.2.19 on 2022-10-04 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20221003_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
