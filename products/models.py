from django.db import models

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name

class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    stock_qty = models.PositiveIntegerField(default=0)
    reserved_qty = models.PositiveIntegerField(default=0)

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
        if self.stock_qty >= quantity:
            self.stock_qty -= quantity
            self.reserved_qty = max(0, self.reserved_qty - quantity)
            self.save()
            return True
        return False