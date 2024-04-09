# shop/urls.py
from django.urls import path

from shop.views import home, shop, product, get_cart_data, add_to_cart, get_session_cart_items, add_to_wishlist, show_wishlist, delete_from_cart

app_name = 'shop'

urlpatterns = [
    path('', home, name='home'),
    path('shop', shop, name='shop'),
    path('product-detail/<int:product_id>/', product, name='product-detail'),
    path('get-cart-items/', get_cart_data, name='cart'),
    path('get-cart-items-count/', get_session_cart_items, name='cart-items-count'),
    path('add-to-cart/<int:product_id>', add_to_cart, name='add-to-cart'),
    path('delete-item-from-cart/<int:product_id>', delete_from_cart, name='delete-item-from-cart'),
    path('add-to-wishlist/<int:product_id>', add_to_wishlist, name='add-to-wishlist'),
    path('go-to-wishlist/', show_wishlist, name='wishlist'),
]
