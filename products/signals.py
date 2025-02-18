from django.contrib.sessions.models import Session
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Product

@receiver(pre_delete, sender=Session)
def release_reserved_quantities(sender, instance, **kwargs):
    """Release reserved quantities when a session is deleted"""
    try:
        # Get the bag from the session
        session_data = instance.get_decoded()
        bag = session_data.get('bag', {})
        
        # Release reserved quantities for each product in the bag
        for item_id, item_data in bag.items():
            try:
                product = Product.objects.get(pk=item_id)
                if isinstance(item_data, dict):
                    # Product with sizes
                    total_qty = sum(item_data.get('items_by_size', {}).values())
                else:
                    # Product without sizes
                    total_qty = item_data
                    
                # Decrease reserved quantity
                product.reserved_qty = max(0, product.reserved_qty - total_qty)
                product.save()
            except Product.DoesNotExist:
                continue
    except Exception:
        # If there's any error, we don't want to prevent session deletion
        pass
