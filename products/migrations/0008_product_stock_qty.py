# Generated by Django 5.1.4 on 2025-01-12 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_remove_product_available_stock_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock_qty',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
