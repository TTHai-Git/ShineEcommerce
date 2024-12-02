# Generated by Django 5.0.3 on 2024-11-30 06:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cosmetics', '0039_imagesofcomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_url', models.URLField(null=True)),
                ('file_name', models.CharField(max_length=100, null=True)),
                ('file_public_id', models.CharField(max_length=100, null=True)),
                ('file_asset_id', models.CharField(max_length=100, null=True)),
                ('file_resource_type', models.CharField(max_length=50, null=True)),
                ('file_type', models.CharField(max_length=50, null=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cosmetics.comment')),
            ],
        ),
        migrations.DeleteModel(
            name='ImagesOfComment',
        ),
    ]