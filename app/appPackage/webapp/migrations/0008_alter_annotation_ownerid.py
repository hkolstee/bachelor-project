# Generated by Django 3.2.3 on 2021-06-14 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0007_annotation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='ownerid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.component'),
        ),
    ]
