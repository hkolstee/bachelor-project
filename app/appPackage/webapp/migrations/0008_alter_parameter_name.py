# Generated by Django 3.2.3 on 2021-05-28 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0007_alter_relation_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='name',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
    ]
