from django.contrib.sessions.models import Session
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from .models import Product
import requests

@receiver(post_save, sender=Product)
def validate_product_image(sender, instance, **kwargs):
    """Check and replace invalid product images with noimage.png."""
    if kwargs.get('update_fields') and 'image' not in kwargs['update_fields']:
        return
        
    # Skip if already processing the image
    if getattr(instance, '_validating_image', False):
        return

    if instance.image:
        needs_update = False
        if isinstance(instance.image, str):
            needs_update = True
        elif hasattr(instance.image, 'url'):
            try:
                image_url = str(instance.image.url)
                response = requests.head(image_url)
                if response.status_code != 200:
                    needs_update = True
            except:
                needs_update = True
    else:
        needs_update = True

    if needs_update:
        # Set flag to prevent recursion
        instance._validating_image = True
        instance.image = 'media/noimage.png'
        instance.save(update_fields=['image'])
        instance._validating_image = False
        print(f'Product ID {instance.id}: Image updated to noimage.png')

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
        # Session deletion will proceed even in the event of an error.
        pass
