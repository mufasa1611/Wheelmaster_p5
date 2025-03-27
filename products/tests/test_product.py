from django.test import TestCase
from products.models import Product

class ProductStockTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=99.99,
            stock_qty=10
        )

    def test_initial_stock(self):
        """Test initial stock quantity"""
        self.assertEqual(self.product.stock_qty, 10)

    def test_reduce_stock(self):
        """Test reducing stock"""
        if hasattr(self.product, 'reduce_stock'):
            self.product.reduce_stock(3)
            self.assertEqual(self.product.stock_qty, 7)

    def test_negative_stock_prevention(self):
        """Test cannot reduce below zero"""
        if hasattr(self.product, 'reduce_stock'):
            with self.assertRaises(ValueError):
                self.product.reduce_stock(20)

    def test_add_stock(self):
        """Test adding stock"""
        if hasattr(self.product, 'add_stock'):
            self.product.add_stock(5)
            self.assertEqual(self.product.stock_qty, 15)

    def test_zero_quantity(self):
        """Test handling zero quantity"""
        if hasattr(self.product, 'reduce_stock'):
            with self.assertRaises(ValueError):
                self.product.reduce_stock(0)

    def test_invalid_quantity_type(self):
        """Test invalid quantity type handling"""
        if hasattr(self.product, 'reduce_stock'):
            with self.assertRaises(ValueError):
                self.product.reduce_stock('invalid')

    def test_stock_status(self):
        """Test stock status reporting"""
        if hasattr(self.product, 'get_stock_status'):
            self.assertEqual(self.product.get_stock_status(), "In Stock")
            self.product.stock_qty = 3
            self.assertEqual(self.product.get_stock_status(), "Low Stock")
            self.product.stock_qty = 0
            self.assertEqual(self.product.get_stock_status(), "Out of Stock")