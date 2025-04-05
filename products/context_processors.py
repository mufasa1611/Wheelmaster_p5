from django.core.cache import cache
from .models import Category

def categories_processor(request):
    nav_categories = cache.get('nav_categories')

    if nav_categories is None:
        # Fetch main categories
        main_categories = Category.objects.filter(parent=None, is_active=True).order_by('name')

        nav_categories = {}
        for main in main_categories:
            # Recursively fetch children
            children = build_category_tree(main)
            nav_categories[main] = children

        cache.set('nav_categories', nav_categories, 3600)

    return {'nav_categories': nav_categories}

def build_category_tree(category):
    """
    Recursively build category trees with nested children.
    """
    children = category.children.filter(is_active=True).order_by('name')
    return [
        {
            'category': child,
            'children': build_category_tree(child)  # Recursively include deeper levels
        }
        for child in children
    ]
