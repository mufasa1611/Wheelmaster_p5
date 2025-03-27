from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product

def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url', '/')
    size = request.POST.get('product_size', None)

    # Validate size if the product requires sizes
    if product.has_sizes and not size:
        messages.error(request, 'Please select a size before adding to the bag.')
        return redirect(redirect_url)

    # Validate stock availability
    if quantity > product.available_qty:
        messages.error(request, f'Sorry, only {product.available_qty} units available.')
        return redirect(redirect_url)

    # Reserve the stock
    if not product.reserve_stock(quantity):
        messages.error(request, 'Sorry, the requested quantity is no longer available.')
        return redirect(redirect_url)

    bag = request.session.get('bag', {})

    if size:
        if item_id in bag:
            if not isinstance(bag[item_id], dict):
                bag[item_id] = {'items_by_size': {}}
        else:
            bag[item_id] = {'items_by_size': {}}

        if size in bag[item_id]['items_by_size']:
            bag[item_id]['items_by_size'][size] += quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
        else:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
    else:
        if item_id in bag:
            if isinstance(bag[item_id], dict):
                bag[item_id] = bag[item_id].get('items_by_size', {}).get('default', 0) + quantity
            else:
                bag[item_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag[item_id] = quantity
            messages.success(request, f'Added {product.name} to your bag')

    request.session['bag'] = bag
    return redirect(redirect_url)

def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity', 0))
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        # Get current quantity in bag
        current_qty = 0
        if size:
            if item_id in bag and isinstance(bag[item_id], dict):
                current_qty = bag[item_id]['items_by_size'].get(size, 0)
        else:
            if item_id in bag:
                current_qty = bag[item_id] if not isinstance(bag[item_id], dict) else 0

        # Calculate quantity difference
        qty_difference = quantity - current_qty

        # If increasing quantity, validate stock and reserve it
        if qty_difference > 0:
            if qty_difference > product.available_qty:
                messages.error(request, f'Sorry, only {product.available_qty} additional units available.')
                return HttpResponse(status=400)
            if not product.reserve_stock(qty_difference):
                messages.error(request, 'Sorry, the requested quantity is no longer available.')
                return HttpResponse(status=400)
        # If decreasing quantity, release the correct amount of stock
        elif qty_difference < 0:
            product.release_stock(abs(qty_difference))

        # Update the bag with new quantity
        if size:
            if quantity > 0:
                if item_id not in bag:
                    bag[item_id] = {'items_by_size': {}}
                elif not isinstance(bag[item_id], dict):
                    bag[item_id] = {'items_by_size': {}}
                bag[item_id]['items_by_size'][size] = quantity
            else:
                del bag[item_id]['items_by_size'][size]
                if not bag[item_id]['items_by_size']:
                    bag.pop(item_id)
        else:
            if quantity > 0:
                bag[item_id] = quantity
            else:
                bag.pop(item_id)

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error updating bag: {str(e)}')
        return HttpResponse(status=500)

def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        bag = request.session.get('bag', {})
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']

        if size:
            if item_id in list(bag.keys()):
                # Get quantity before removing
                quantity_to_release = bag[item_id]['items_by_size'].get(size, 0)
                # Release the stock
                if quantity_to_release > 0:
                    product.release_stock(quantity_to_release)
                # Remove from bag
                del bag[item_id]['items_by_size'][size]
                if not bag[item_id]['items_by_size']:
                    bag.pop(item_id)
                messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
        else:
            if item_id in list(bag.keys()):
                # Get quantity before removing
                quantity_to_release = bag[item_id] if isinstance(bag[item_id], int) else sum(bag[item_id].get('items_by_size', {}).values())
                # Release the stock
                if quantity_to_release > 0:
                    product.release_stock(quantity_to_release)
                # Remove from bag
                bag.pop(item_id)
                messages.success(request, f'Removed {product.name} from your bag')

        request.session['bag'] = bag
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(status=200)
        return redirect(reverse('view_bag'))

    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(status=404)
        return redirect(reverse('view_bag'))
    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(status=500)
        return redirect(reverse('view_bag'))

def get_bag_quantities(request):
    """Return the current quantities in the shopping bag as JSON"""
    bag = request.session.get('bag', {})
    quantities = {}
    
    for item_id, item_data in bag.items():
        if isinstance(item_data, int):
            quantities[item_id] = {'default': item_data}
        else:
            quantities[item_id] = item_data
    
    return JsonResponse(quantities)
