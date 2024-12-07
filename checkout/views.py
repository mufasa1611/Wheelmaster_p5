import os, stripe, json
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from django.contrib import messages
from bag.contexts import bag_contents
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings

def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')
    stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')

    if request.method == 'POST':
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            
            # Ensure order totals are updated after all line items are saved
            order.update_total()
            return redirect(reverse('checkout_success', args=[order.order_number]))
    else:
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency='eur',
        )

        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. \
                Did you forget to set it in your environment?')

        order_form = OrderForm()
        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

        return render(request, template, context)

 ## Checkout test Success View
@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        # Check if order with this payment intent already exists
        if Order.objects.filter(stripe_pid=pid).exists():
            return HttpResponse(status=400)
            
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username 
            if request.user.is_authenticated 
            else 'AnonymousUser'
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    # Send confirmation email
    subject = f'Wheelmaster - Order Confirmation {order_number}'
    message = (
        f"Thank you for your order!\n\n"
        f"Order Number: {order.order_number}\n"
        f"Order Date: {order.date}\n\n"
        f"Order Total: €{order.order_total}\n"
        f"Delivery: €{order.delivery_cost}\n"
        f"Grand Total: €{order.grand_total}\n\n"
        f"Your order will be shipped to:\n"
        f"{order.street_address1}\n"
        f"{order.town_or_city}\n"
        f"{order.country}\n\n"
        f"We've got your phone number on file as {order.phone_number}\n\n"
        f"If you have any questions, please contact us!\n\n"
        f"Thank you for shopping with Wheelmaster!"
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email]
    )

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email has been sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)