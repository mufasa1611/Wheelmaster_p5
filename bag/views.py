from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product

def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    try:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity', 1))
        redirect_url = request.POST.get('redirect_url')
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        if size:
            if item_id in list(bag.keys()):
                if size in bag[item_id]['items_by_size'].keys():
                    bag[item_id]['items_by_size'][size] += quantity
                    msg = (
                        f'Updated size {size.upper()} {product.name} '
                        f'quantity to {bag[item_id]["items_by_size"][size]}'
                    )
                    messages.success(request, msg)
                else:
                    bag[item_id]['items_by_size'][size] = quantity
                    msg = (
                        f'Added size {size.upper()} {product.name} to '
                        f'your bag'
                    )
                    messages.success(request, msg)
            else:
                bag[item_id] = {'items_by_size': {size: quantity}}
                msg = (
                    f'Added size {size.upper()} {product.name} to '
                    f'your bag'
                )
                messages.success(request, msg)
        else:
            if item_id in list(bag.keys()):
                if isinstance(bag[item_id], dict):
                    # If the existing item has a size structure
                    bag[item_id] = quantity
                else:
                    # If the existing item is a simple quantity
                    bag[item_id] += quantity
                msg = (
                    f'Updated {product.name} quantity to '
                    f'{bag[item_id]}'
                )
                messages.success(request, msg)
            else:
                bag[item_id] = quantity
                msg = f'Added {product.name} to your bag'
                messages.success(request, msg)

        request.session['bag'] = bag
        return redirect(redirect_url)
        
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect(reverse('view_bag'))
    except Exception as e:
        messages.error(request, f'Error adding item to bag: {e}')
        return redirect(reverse('view_bag'))

def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity', 0))
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        if size:
            if quantity > 0:
                if item_id in list(bag.keys()):
                    bag[item_id]['items_by_size'][size] = quantity
                    msg = (
                        f'Updated size {size.upper()} {product.name} '
                        f'quantity to {bag[item_id]["items_by_size"][size]}'
                    )
                    messages.success(request, msg)
            else:
                del bag[item_id]['items_by_size'][size]
                if not bag[item_id]['items_by_size']:
                    bag.pop(item_id)
                msg = (
                    f'Removed size {size.upper()} {product.name} from '
                    f'your bag'
                )
                messages.success(request, msg)
        else:
            if quantity > 0:
                bag[item_id] = quantity
                msg = (
                    f'Updated {product.name} quantity to '
                    f'{bag[item_id]}'
                )
                messages.success(request, msg)
            else:
                bag.pop(item_id)
                msg = (
                    f'Removed {product.name} from your bag'
                )
                messages.success(request, msg)

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
        messages.error(request, f'Error adjusting bag: {e}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(status=500)
        return redirect(reverse('view_bag'))

def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        if size:
            if item_id in list(bag.keys()):
                del bag[item_id]['items_by_size'][size]
                if not bag[item_id]['items_by_size']:
                    bag.pop(item_id)
                msg = (
                    f'Removed size {size.upper()} {product.name} from '
                    f'your bag'
                )
                messages.success(request, msg)
        else:
            if item_id in list(bag.keys()):
                bag.pop(item_id)
                msg = (
                    f'Removed {product.name} from your bag'
                )
                messages.success(request, msg)

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
