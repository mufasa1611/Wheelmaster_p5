# Generated by Django 5.1.2 on 2024-12-30 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_has_sizes'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock_qty',
            field=models.IntegerField(default=0),
        ),
    ]
