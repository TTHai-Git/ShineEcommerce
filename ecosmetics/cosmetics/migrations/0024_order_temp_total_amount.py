# Generated by Django 5.0.3 on 2024-11-07 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cosmetics', '0023_order_shipment_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='temp_total_amount',
            field=models.FloatField(default=0, null=True),
        ),
    ]
