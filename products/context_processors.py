from django.core.cache import cache
from django.db.models import Count, Q
from .models import Category

def categories_processor(request):
    """
    Context processor to provide active categories for navigation with caching
    """
    # get categories from cache
    nav_categories = cache.get('nav_categories')
    
    if nav_categories is None:
        # Get main categories (those with no parent and active children)
        main_categories = Category.objects.filter(
            parent=None,
            is_active=True,
        ).exclude(
            children=None
        ).order_by('name')

        nav_categories = {}
        for main in main_categories:
            # Get all active children that are not parents themselves
            direct_children = main.children.filter(
                is_active=True,
                children=None  # Only get children that don't have their own children
            )
            
            # Get parent categories (children that have their own children)
            parent_categories = main.children.filter(
                is_active=True,
                children__isnull=False
            ).distinct()
            
            # Combine direct children and parent categories
            all_children = list(direct_children)
            
            # For each parent category, add it and its children
            for parent in parent_categories:
                all_children.append(parent)  # Add the parent category itself
            
            if all_children:
                nav_categories[main] = sorted(all_children, key=lambda x: x.name)

        # Cache the result for 1 hour (3600 seconds)
        cache.set('nav_categories', nav_categories, 3600)

    return {'nav_categories': nav_categories}
