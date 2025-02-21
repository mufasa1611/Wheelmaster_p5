from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('inventory/', views.inventory_management, name='inventory_management'),
    path('adjust_stock/', views.adjust_stock, name='adjust_stock'),
    path('stock/<int:product_id>/', views.get_stock_info, name='get_stock_info'),
]
