# Generated by Django 3.2.3 on 2021-05-31 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='attributeid',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='component',
            name='componentid',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='modelrepresentation',
            name='file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='webapp.modelfile'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='operationid',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='parameterid',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='relation',
            name='relationid',
            field=models.CharField(max_length=20),
        ),
    ]