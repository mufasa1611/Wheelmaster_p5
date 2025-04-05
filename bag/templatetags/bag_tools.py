from django import template
import math

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    return multiply(price, quantity)