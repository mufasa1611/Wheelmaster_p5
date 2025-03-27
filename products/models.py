from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.cache import cache

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.parent:
            return f'{self.parent.friendly_name} - {self.friendly_name}'
        return self.friendly_name or self.name

    def get_friendly_name(self):
        return self.friendly_name or self.name

    @property
    def is_main_category(self):
        """Check if category is a main category that should appear in navbar"""
        # A main category is one that has no parent and has active children
        return self.parent is None and self.children.filter(is_active=True).exists()

    @property
    def is_parent_category(self):
        """Check if category is a parent category (not in navbar)"""
        # A parent category is one that has no parent but also no children
        return self.parent is None and not self.children.filter(is_active=True).exists()
        
    def get_children(self):
        """Get all active child categories"""
        return self.children.filter(is_active=True)

    def get_all_children(self):
        """Get all child categories regardless of active status"""
        return self.children.all()

    def get_active_products(self):
        """Get all products from this category and its children"""
        if self.is_parent_category:
            # If parent, get products from self and all active children
            child_categories = self.get_children()
            return Product.objects.filter(
                Q(category=self) |
                Q(category__in=child_categories)
            )
        # If child, just get own products
        return self.product_set.all()

    def clean(self):
        """Validate category hierarchy"""
        super().clean()
        
        # Ensure friendly name is set
        if not self.friendly_name:
            self.friendly_name = self.name.replace('_', ' ').title()
            
        if self.parent:
            # Check if parent is already a child category
            if self.parent.parent is not None:
                raise ValidationError({
                    'parent': 'Cannot set a child category as parent. Only main categories can be parents.'
                })
            
            # Check for circular reference
            if self.pk and self.parent.pk == self.pk:
                raise ValidationError({
                    'parent': 'A category cannot be its own parent.'
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Clear the navigation cache when a category is saved
        cache.delete('nav_categories')

    @classmethod
    def get_nav_categories(cls):
        """Get categories for navigation with caching"""
        # Try to get categories from cache
        nav_categories = cache.get('nav_categories')
        
        if nav_categories is None:
            # If not in cache, generate the dictionary
            parent_categories = cls.objects.filter(
                parent=None,
                is_active=True
            ).order_by('name')

            nav_categories = {}
            for parent in parent_categories:
                active_children = parent.children.filter(is_active=True).order_by('name')
                if active_children.exists():
                    nav_categories[parent] = active_children

            # Cache the result for 1 hour (3600 seconds)
            cache.set('nav_categories', nav_categories, 3600)

        return nav_categories

class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    stock_qty = models.PositiveIntegerField(default=0)
    reserved_qty = models.PositiveIntegerField(default=0)
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    

    def __str__(self):
        return self.name

    @property
    def available_qty(self):
        return max(0, self.stock_qty - self.reserved_qty)

    def reserve_stock(self, quantity):
        """Reserve stock for a product"""
        if quantity <= self.available_qty:
            self.reserved_qty += quantity
            self.save()
            return True
        return False

    def release_stock(self, quantity):
        """Release previously reserved stock"""
        self.reserved_qty = max(0, self.reserved_qty - quantity)
        self.save()

    def reduce_stock(self, quantity):
        """Reduce stock after successful order"""
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a valid number")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if self.stock_qty >= quantity:
            self.stock_qty -= quantity
            self.reserved_qty = max(0, self.reserved_qty - quantity)
            self.save()
            return True
        raise ValueError("Insufficient stock available")