from django.test import TestCase
from products.models import Category

class TestCategoryHierarchy(TestCase):
    def setUp(self):
        # Create parent categories
        self.wheelbarrows = Category.objects.create(
            pk=100,  # Use high PKs to avoid conflicts
            name="test_wheelbarrows",
            friendly_name="Test Wheelbarrows",
            is_active=True
        )
        
        # Create child categories
        self.standard_wheelbarrows = Category.objects.create(
            pk=101,
            name="test_standard_wheelbarrows",
            friendly_name="Test Wheelbarrows - Standard Wheelbarrows",
            is_active=True,
            parent=self.wheelbarrows
        )
        
        self.kids_wheelbarrows = Category.objects.create(
            pk=102,
            name="test_kids_wheelbarrows",
            friendly_name="Test Wheelbarrows - Kids Wheelbarrows",
            is_active=True,
            parent=self.wheelbarrows
        )

    def test_parent_child_relationship(self):
        """Test that parent-child relationships work correctly"""
        # Test parent category properties
        self.assertTrue(self.wheelbarrows.is_parent)
        self.assertTrue(self.wheelbarrows.has_children)
        self.assertEqual(self.wheelbarrows.get_children().count(), 2)
        
        # Test child category properties
        self.assertFalse(self.standard_wheelbarrows.is_parent)
        self.assertFalse(self.standard_wheelbarrows.has_children)
        self.assertEqual(self.standard_wheelbarrows.parent, self.wheelbarrows)
        
    def test_active_status(self):
        """Test that is_active flag works with parent-child relationships"""
        # Count only our test categories
        initial_active = Category.objects.filter(
            name__startswith='test_',
            is_active=True
        ).count()
        self.assertEqual(initial_active, 3)
        
        # Deactivate parent
        self.wheelbarrows.is_active = False
        self.wheelbarrows.save()
        
        # Check that get_children respects is_active flag
        active_after_parent = Category.objects.filter(
            name__startswith='test_',
            is_active=True
        ).count()
        self.assertEqual(active_after_parent, 2)
        
        # Deactivate child
        self.standard_wheelbarrows.is_active = False
        self.standard_wheelbarrows.save()
        
        # Check active children count
        self.assertEqual(self.wheelbarrows.get_children().count(), 1)
        
    def test_friendly_name_formatting(self):
        """Test that friendly names are formatted correctly"""
        # Test parent category
        self.assertEqual(self.wheelbarrows.get_friendly_name(), "Test Wheelbarrows")
        
        # Test child category
        self.assertEqual(
            self.standard_wheelbarrows.get_friendly_name(),
            "Test Wheelbarrows - Standard Wheelbarrows"
        )
