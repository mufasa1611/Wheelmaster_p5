import os
import json

from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings

import stripe

from products.models import Product
from .forms import OrderForm
from .models import Order, OrderLineItem
from bag.contexts import bag_contents


REQUIRED_FORM_KEYS = [
    'full_name', 'email', 'phone_number', 'country',
    'postcode', 'town_or_city', 'street_address1',
    'street_address2', 'county',
]

def checkout(request):
    """Handle checkout page rendering and order submission."""
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse('products'))

    stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')
    stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')

    if not stripe_public_key:
        messages.warning(
            request, "Stripe public key is missing. Did you set it in your environment?"
        )

    if request.method == 'POST':
        return process_checkout(request, bag)

    return render_checkout_page(request, bag, stripe_public_key, stripe_secret_key)


def process_checkout(request, bag):
    """Process the checkout form and save the order."""
    try:
        form_data = {key: request.POST[key] for key in REQUIRED_FORM_KEYS}
    except KeyError as e:
        messages.error(request, f"Missing required field: {e}." )
        return redirect(reverse('checkout'))

    order_form = OrderForm(form_data)
    if not order_form.is_valid():
        messages.error(request, "There was an error with your form. Please try again.")
        return redirect(reverse('checkout'))

    order = order_form.save()
    try:
        add_order_items(order, bag)
    except Product.DoesNotExist:
        messages.error(
            request,
            "A product in your bag couldn't be found in our database. Please contact support."
        )
        order.delete()
        return redirect(reverse('view_bag'))

    order.update_total()
    return redirect(reverse('checkout_success', args=[order.order_number]))


def add_order_items(order, bag):
    """Add items to the order from the shopping bag."""
    for item_id, item_data in bag.items():
        try:
            product = Product.objects.get(id=item_id)
        except Product.DoesNotExist:
            raise
        if isinstance(item_data, int):
            OrderLineItem.objects.create(order=order, product=product, quantity=item_data)
        else:
            for size, quantity in item_data.get('items_by_size', {}).items():
                OrderLineItem.objects.create(
                    order=order, product=product, quantity=quantity, product_size=size
                )


def render_checkout_page(request, bag, stripe_public_key, stripe_secret_key):
    """Render the checkout page with Stripe payment intent."""
    if not stripe_secret_key:
        messages.error(request, "Stripe secret key is missing. Please contact support.")
        return redirect(reverse('view_bag'))

    stripe.api_key = stripe_secret_key
    current_bag = bag_contents(request)
    total = current_bag.get('grand_total', 0)
    stripe_total = round(total * 100)

    try:
        intent = stripe.PaymentIntent.create(amount=stripe_total, currency='eur')
    except stripe.error.StripeError:
        messages.error(request, "Stripe error occurred. Please try again later.")
        return redirect(reverse('view_bag'))

    context = {
        'order_form': OrderForm(),
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }
    return render(request, 'checkout/checkout.html', context)


@require_POST
def cache_checkout_data(request):
    """Cache checkout data in Stripe's metadata for the PaymentIntent."""
    client_secret = request.POST.get('client_secret')
    if not client_secret or '_secret' not in client_secret:
        messages.error(request, "Invalid payment data. Please try again.")
        return HttpResponse(status=400)

    try:
        pid = client_secret.split('_secret')[0]
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                'bag': json.dumps(request.session.get('bag', {})),
                'save_info': request.POST.get('save_info'),
                'username': (
                    request.user.username if request.user.is_authenticated else 'AnonymousUser'
                ),
            }
        )
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, "Sorry, your payment cannot be processed right now. Please try again later.")
        return HttpResponse(content=str(e), status=400)


def checkout_success(request, order_number):
    """Handle successful checkouts and send confirmation email."""
    order = get_object_or_404(Order, order_number=order_number)

    # Send confirmation email
    try:
        send_order_confirmation_email(order)
    except Exception:
        messages.error(request, "There was an issue sending your confirmation email.")

    messages.success(
        request,
        f"Order successfully processed! Your order number is {order_number}. "
        f"A confirmation email has been sent to {order.email}.")
    if 'bag' in request.session:
        del request.session['bag']

    context = {'order': order}
    return render(request, 'checkout/checkout_success.html', context)


def send_order_confirmation_email(order):
    """Send an order confirmation email to the customer."""
    subject = f"Wheelmaster - Order Confirmation {order.order_number}"
    message = (
        f"Thank you for your order!\n\n"
        f"Order Number: {order.order_number}\n"
        f"Order Date: {order.date}\n\n"
        f"Order Total: €{order.order_total}\n"
        f"Delivery: €{order.delivery_cost}\n"
        f"Grand Total: €{order.grand_total}\n\n"
        f"Your order will be shipped to:\n"
        f"{order.street_address1}\n{order.town_or_city}\n{order.country}\n\n"
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
