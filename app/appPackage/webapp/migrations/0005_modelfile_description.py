# Generated by Django 3.2.3 on 2021-06-03 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_auto_20210602_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelfile',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]