from django.db import migrations

def update_categories_and_products(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')

    # First, create the main categories
    main_categories = {
        'wheelbarrows': 'Wheelbarrows',
        'transport_trolleys': 'Transport Trolleys',
        'scaffolding_construction': 'Scaffolding & Construction Tools'
    }

    # Create or update categories
    for main_name, main_friendly in main_categories.items():
        Category.objects.update_or_create(
            name=main_name,
            defaults={'friendly_name': main_friendly}
        )

    # Then create subcategories
    subcategories = {
        'wheelbarrows': [
            ('standard_wheelbarrows', 'Standard Wheelbarrows'),
            ('kids_wheelbarrows', 'Kids Wheelbarrows')
        ],
        'transport_trolleys': [
            ('folding_trolleys', 'Folding Trolleys'),
            ('heavy_duty_trolleys', 'Heavy-Duty Trolleys')
        ],
        'scaffolding_construction': [
            ('scaffolding_kits', 'Scaffolding Kits'),
            ('concrete_mixers', 'Concrete Mixers')
        ]
    }

    # Create subcategories
    for main_name, subs in subcategories.items():
        main_category = Category.objects.get(name=main_name)
        for sub_name, sub_friendly in subs:
            Category.objects.update_or_create(
                name=sub_name,
                defaults={'friendly_name': f'{main_category.friendly_name} - {sub_friendly}'}
            )

    # Product data
    products_data = [
        {
            'id': 1,
            'sku': 'Z029/10/00/106',
            'name': 'Classic Gardener',
            'description': 'A robust, lightweight wheelbarrow for general gardening tasks.',
            'price': 46.80,  
            'category': 'standard_wheelbarrows',
            'rating': 4.5
        },
        {
            'id': 2,
            'sku': 'Z030/20/00/107',
            'name': 'Heavy Hauler',
            'description': 'Durable construction for heavy-duty transport.',
            'price': 70.20, 
            'category': 'standard_wheelbarrows',
            'rating': 4.7
        },
        {
            'id': 3,
            'sku': 'Z031/10/00/201',
            'name': 'Peter',
            'description': 'A colorful, sturdy wheelbarrow for children.',
            'price': 23.40, 
            'category': 'kids_wheelbarrows',
            'rating': 4.8
        },
        {
            'id': 4,
            'sku': 'Z032/15/00/202',
            'name': 'Heidi',
            'description': 'Small, lightweight wheelbarrow perfect for kids.',
            'price': 21.06,  
            'category': 'kids_wheelbarrows',
            'rating': 4.6
        },
        {
            'id': 5,
            'sku': 'Z040/20/00/301',
            'name': 'Easy Fold',
            'description': 'Compact, foldable trolley for storage efficiency.',
            'price': 58.50,  
            'category': 'folding_trolleys',
            'rating': 4.4
        },
        {
            'id': 6,
            'sku': 'Z041/25/00/302',
            'name': 'Travel Mate',
            'description': 'Lightweight trolley designed for travel purposes.',
            'price': 64.35,  
            'category': 'folding_trolleys',
            'rating': 4.5
        },
        {
            'id': 7,
            'sku': 'Z042/30/00/401',
            'name': 'Titan Cart',
            'description': 'A heavy-duty trolley for industrial use.',
            'price': 105.30,  
            'category': 'heavy_duty_trolleys',
            'rating': 4.8
        },
        {
            'id': 8,
            'sku': 'Z043/35/00/402',
            'name': 'Load Pro',
            'description': 'Designed for moving heavy materials over rough terrain.',
            'price': 117.00,  
            'category': 'heavy_duty_trolleys',
            'rating': 4.7
        },
        {
            'id': 9,
            'sku': 'Z050/40/00/501',
            'name': 'Quick-Build Scaffold',
            'description': 'Modular scaffolding for easy assembly.',
            'price': 140.40, 
            'category': 'scaffolding_kits',
            'rating': 4.6
        },
        {
            'id': 10,
            'sku': 'Z051/45/00/502',
            'name': 'Pro-Level Scaffold',
            'description': 'Premium scaffolding for professional use.',
            'price': 175.50, 
            'category': 'scaffolding_kits',
            'rating': 4.9
        },
        {
            'id': 11,
            'sku': 'Z060/50/00/601',
            'name': 'Rapid Mixer',
            'description': 'Portable concrete mixer with fast operation.',
            'price': 234.00,  
            'category': 'concrete_mixers',
            'rating': 4.8
        },
        {
            'id': 12,
            'sku': 'Z061/55/00/602',
            'name': 'Durable Mixer',
            'description': 'Long-lasting concrete mixer for large projects.',
            'price': 292.50,  
            'category': 'concrete_mixers',
            'rating': 4.7
        }
    ]

    # Update or create products
    for product_data in products_data:
        category = Category.objects.get(name=product_data['category'])
        Product.objects.update_or_create(
            id=product_data['id'],
            defaults={
                'sku': product_data['sku'],
                'name': product_data['name'],
                'description': product_data['description'],
                'price': product_data['price'],
                'category': category,
                'rating': product_data['rating']
            }
        )

def reverse_migration(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    
    # Delete all products created in this migration
    Product.objects.filter(id__in=range(1, 13)).delete()
    
    # Delete categories
    Category.objects.filter(name__in=[
        'wheelbarrows', 'transport_trolleys', 'scaffolding_construction',
        'standard_wheelbarrows', 'kids_wheelbarrows', 'folding_trolleys',
        'heavy_duty_trolleys', 'scaffolding_kits', 'concrete_mixers'
    ]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0009_product_reserved_qty'),
    ]

    operations = [
        migrations.RunPython(update_categories_and_products, reverse_migration),
    ]
