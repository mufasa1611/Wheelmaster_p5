from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.db.models.functions import Lower
from .models import Product, Category
from .forms import ProductForm
from django.http import JsonResponse
import json

 # A view to show all products, including sorting and search queries 

def all_products(request):

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None
    if request.GET:
        # Sorting
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            elif sortkey == 'category':
                 sortkey = 'category__name'
            elif sortkey == 'price':
                 sortkey = 'price'
            elif sortkey == 'rate':
                 products = products.annotate(rate=F('rating'))
                 sortkey = 'rate'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
            
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)
    current_sorting = f'{sort}_{direction}'
    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request,
                           ('Failed to add product. '
                            'Please ensure the form is valid.'))
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)

@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)

@login_required
def delete_product(request, product_id):
    """ Delete a product from the store using AJAX """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Only store owners can delete products'}, status=403)
    
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return JsonResponse({'success': 'Product deleted successfully'})

@login_required
def inventory_management(request):
    """A view to manage product inventory"""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    products = Product.objects.all().order_by('category', 'name')
    template = 'products/inventory.html'
    context = {
        'products': products,
    }

    return render(request, template, context)


@login_required
def adjust_stock(request):
    """Adjust product stock levels"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)

    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 0))
        action = data.get('action')

        if not all([product_id, quantity, action]) or action not in ['add', 'reduce']:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        product = get_object_or_404(Product, id=product_id)

        if action == 'add':
            product.stock_qty += quantity
        else:  # reduce
            if product.stock_qty - quantity < product.reserved_qty:
                return JsonResponse({
                    'error': 'Cannot reduce stock below reserved quantity'
                }, status=400)
            product.stock_qty = max(0, product.stock_qty - quantity)

        product.save()

        return JsonResponse({
            'stock_qty': product.stock_qty,
            'reserved_qty': product.reserved_qty,
            'available_qty': product.stock_qty - product.reserved_qty
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid quantity value'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_stock_info(request, product_id):
    """Get stock information for a product"""
    try:
        product = get_object_or_404(Product, pk=product_id)
        return JsonResponse({
            'stock_qty': product.stock_qty,
            'reserved_qty': product.reserved_qty,
            'available_qty': product.stock_qty - product.reserved_qty
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)