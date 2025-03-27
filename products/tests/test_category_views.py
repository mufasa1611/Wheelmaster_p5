from django.test import TestCase, Client
from django.urls import reverse
from products.models import Category, Product

class TestCategoryViews(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create parent category
        self.transport = Category.objects.create(
            pk=200,  # Use high PKs to avoid conflicts
            name="test_transport_trolleys",
            friendly_name="Test Transport Trolleys",
            is_active=True
        )
        
        # Create child categories
        self.folding = Category.objects.create(
            pk=201,
            name="test_folding_trolleys",
            friendly_name="Test Transport Trolleys - Folding Trolleys",
            is_active=True,
            parent=self.transport
        )
        
        self.heavy_duty = Category.objects.create(
            pk=202,
            name="test_heavy_duty_trolleys",
            friendly_name="Test Transport Trolleys - Heavy-Duty Trolleys",
            is_active=True,
            parent=self.transport
        )
        
        # Create some test products
        Product.objects.create(
            pk=1000,  # High PK to avoid conflicts
            name="Test Parent Product",
            category=self.transport,
            price=99.99
        )
        
        Product.objects.create(
            pk=1001,
            name="Test Folding Product",
            category=self.folding,
            price=49.99
        )
        
        Product.objects.create(
            pk=1002,
            name="Test Heavy Duty Product",
            category=self.heavy_duty,
            price=149.99
        )

    def test_category_navigation(self):
        """Test that category navigation shows correct structure"""
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        
        # Check that parent category is in context
        self.assertTrue(any(
            cat['parent'].name == "test_transport_trolleys" 
            for cat in response.context['current_categories']
        ))
        
        # Check that children are properly nested
        parent_category = next(
            cat for cat in response.context['current_categories']
            if cat['parent'].name == "test_transport_trolleys"
        )
        child_names = [child.name for child in parent_category['children']]
        self.assertIn("test_folding_trolleys", child_names)
        self.assertIn("test_heavy_duty_trolleys", child_names)

    def test_parent_category_filter(self):
        """Test filtering by parent category shows all child products"""
        response = self.client.get(f"{reverse('products')}?category=test_transport_trolleys")
        self.assertEqual(response.status_code, 200)
        
        products = list(response.context['products'])
        # Should show all 3 products (parent + 2 children)
        self.assertEqual(len(products), 3)
        product_names = [p.name for p in products]
        self.assertIn("Test Parent Product", product_names)
        self.assertIn("Test Folding Product", product_names)
        self.assertIn("Test Heavy Duty Product", product_names)

    def test_child_category_filter(self):
        """Test filtering by child category shows only those products"""
        response = self.client.get(f"{reverse('products')}?category=test_folding_trolleys")
        self.assertEqual(response.status_code, 200)
        
        products = list(response.context['products'])
        # Should show only 1 product
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Test Folding Product")

    def test_inactive_category(self):
        """Test that inactive categories are properly handled"""
        # Deactivate parent category
        self.transport.is_active = False
        self.transport.save()
        
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        
        # Check that inactive parent is not in navigation
        self.assertFalse(any(
            cat['parent'].name == "test_transport_trolleys" 
            for cat in response.context['current_categories']
        ))
        
        # Try to access the inactive category
        response = self.client.get(f"{reverse('products')}?category=test_transport_trolleys")
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Check that products from inactive categories are not shown in main listing
        response = self.client.get(reverse('products'))
        self.assertFalse(any(
            p.category.name.startswith("test_") 
            for p in response.context['products']
        ))
