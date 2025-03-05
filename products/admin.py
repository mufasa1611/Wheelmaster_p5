from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q, Count
from django.contrib import messages
from django.core.cache import cache
from django import forms
from .models import Product, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'friendly_name', 'parent', 'is_active']
        widgets = {
            'parent': forms.RadioSelect(),
        }
        labels = {
            'name': 'Internal Name',
            'friendly_name': 'Display Name',
            'parent': 'Parent Category',
            'is_active': 'Active',
        }
        help_texts = {
            'parent': 'Select a parent category if this is a subcategory. Leave empty to make this a main/parent category.',
            'name': 'Internal name used in URLs and code.',
            'friendly_name': 'This is how the category will be displayed to customers.',
            'is_active': 'If checked, this category will be visible in the shop.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'parent' in self.fields:
            self.fields['parent'].queryset = Category.objects.filter(parent=None)
            self.fields['parent'].empty_label = "None (Make this a main/parent category)"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ('category_name_display', 'is_active', 'category_type', 'manage_actions')
    list_filter = ('parent', 'is_active')
    search_fields = ('name', 'friendly_name')
    list_per_page = 50
    actions = ['activate_categories', 'deactivate_categories']

    def get_queryset(self, request):
        """Custom queryset to show parent categories first, then their children"""
        qs = super().get_queryset(request)
        return qs.annotate(
            active_children_count=Count('children', filter=Q(children__is_active=True))
        ).order_by('parent', 'name')

    def category_type(self, obj):
        """Display the category type"""
        if obj.parent:
            return format_html('<span style="color: #666;">Child Category</span>')
        elif obj.is_main_category:
            return format_html('<span style="color: #28a745;">Main Category 📱</span>')
        else:
            return format_html('<span style="color: #17a2b8;">Parent Category</span>')
    category_type.short_description = 'Type'

    def category_name_display(self, obj):
        """Display categories in a hierarchical structure"""
        name_display = obj.friendly_name or obj.name
        status_color = '#28a745' if obj.is_active else '#dc3545'
        status_text = '(Active)' if obj.is_active else '(Inactive)'
        
        if obj.parent is None:
            # Parent/Main category 
            child_count = getattr(obj, 'active_children_count', 0)
            if child_count > 0:
                return format_html(
                    '<strong>{}</strong> <span style="color: {};">{}</span> <span style="color: #666;">({} subcategories)</span>',
                    name_display,
                    status_color,
                    status_text,
                    child_count
                )
            return format_html(
                '<strong>{}</strong> <span style="color: {};">{}</span>',
                name_display,
                status_color,
                status_text
            )
        else:
            # Child category 
            parent_name = obj.parent.friendly_name or obj.parent.name
            return format_html(
                '&nbsp;&nbsp;&nbsp;&nbsp;└─ {} <span style="color: {};">{}</span> <span style="color: #666;">(under {})</span>',
                name_display,
                status_color,
                status_text,
                parent_name
            )
    
    category_name_display.short_description = 'Category Structure'

    def manage_actions(self, obj):
        """Display management actions for the category"""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Inactive</span>'
        )
    manage_actions.short_description = 'Status'

    def activate_categories(self, request, queryset):
        """Bulk activate categories"""
        updated = queryset.update(is_active=True)
        cache.delete('nav_categories')  # Clear the navigation cache
        self.message_user(
            request,
            f'{updated} categories have been activated.',
            messages.SUCCESS
        )
    activate_categories.short_description = "Activate selected categories"

    def deactivate_categories(self, request, queryset):
        """Bulk deactivate categories"""
        updated = queryset.update(is_active=False)
        cache.delete('nav_categories')  # Clear the navigation cache
        self.message_user(
            request,
            f'{updated} categories have been deactivated.',
            messages.SUCCESS
        )
    deactivate_categories.short_description = "Deactivate selected categories"

    def save_model(self, request, obj, form, change):
        """Custom save to handle cache clearing"""
        super().save_model(request, obj, form, change)
        cache.delete('nav_categories')  # Clear the navigation cache

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category_display',
        'has_sizes',
        'price',
        'rating',
        'image',
        'stock_qty',
    )

    ordering = ('sku',)
    list_filter = ('category', 'has_sizes')
    search_fields = ('name', 'description')
    list_editable = ('has_sizes', 'stock_qty')

    def category_display(self, obj):
        if obj.category:
            if obj.category.parent:
                return f"{obj.category.parent.friendly_name} > {obj.category.friendly_name}"
            return obj.category.friendly_name
        return "-"
    category_display.short_description = "Category"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            # Show all active categories
            kwargs["queryset"] = Category.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)