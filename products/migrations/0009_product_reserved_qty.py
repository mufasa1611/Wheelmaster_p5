# Generated by Django 5.1.4 on 2025-02-16 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_stock_qty'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='reserved_qty',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
