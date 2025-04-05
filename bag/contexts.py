from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})
    items_to_remove = []

    for item_id, item_data in bag.items():
        try:
            product = get_object_or_404(Product, pk=item_id)

            if isinstance(item_data, int):
                # Validate stock for single item
                quantity = min(item_data, product.stock_qty)
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'max_stock': product.stock_qty
                })
            else:
                # Validate stock for sized items
                for size, quantity in item_data['items_by_size'].items():
                    # Limit quantity to available stock
                    quantity = min(quantity, product.stock_qty)
                    total += quantity * product.price
                    product_count += quantity
                    bag_items.append({
                        'item_id': item_id,
                        'quantity': quantity,
                        'product': product,
                        'size': size,
                        'max_stock': product.stock_qty
                    })

        except Exception as e:
            # Mark item for removal if product doesn't exist
            items_to_remove.append(item_id)
            continue

    # Clean up non-existent items
    for item_id in items_to_remove:
        del bag[item_id]

    request.session['bag'] = bag
    request.session.modified = True

    # Delivery calculations
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context