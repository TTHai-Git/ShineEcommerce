# Generated by Django 5.0.3 on 2024-11-07 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cosmetics', '0025_order_is_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]