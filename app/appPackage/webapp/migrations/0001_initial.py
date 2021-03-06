# Generated by Django 3.2.3 on 2021-05-31 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('componentid', models.CharField(default='', max_length=20)),
                ('name', models.CharField(max_length=45)),
                ('type', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='modelfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operationid', models.CharField(default='', max_length=20)),
                ('name', models.CharField(max_length=45)),
                ('type', models.CharField(max_length=45)),
                ('visiblity', models.CharField(max_length=45)),
                ('ownerid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.component')),
            ],
        ),
        migrations.CreateModel(
            name='relation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationid', models.CharField(default='', max_length=20)),
                ('name', models.CharField(blank=True, max_length=45, null=True)),
                ('type', models.CharField(max_length=45)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source', to='webapp.component')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target', to='webapp.component')),
            ],
        ),
        migrations.CreateModel(
            name='parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameterid', models.CharField(default='', max_length=20)),
                ('name', models.CharField(blank=True, max_length=45, null=True)),
                ('type', models.CharField(max_length=45)),
                ('direction', models.CharField(max_length=45)),
                ('ownerid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.operation')),
            ],
        ),
        migrations.CreateModel(
            name='modelrepresentation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modelid', models.CharField(max_length=45)),
                ('name', models.CharField(max_length=45)),
                ('file', models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to='webapp.modelfile')),
            ],
        ),
        migrations.AddField(
            model_name='component',
            name='modelid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.modelrepresentation'),
        ),
        migrations.CreateModel(
            name='attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributeid', models.CharField(default='', max_length=20)),
                ('name', models.CharField(max_length=45)),
                ('type', models.CharField(max_length=45)),
                ('datatype', models.CharField(blank=True, max_length=45, null=True)),
                ('visibilty', models.CharField(max_length=45)),
                ('ownerid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.component')),
            ],
        ),
    ]
