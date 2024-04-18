# shop/urls.py
from django.urls import path

from shop import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop', views.shop, name='shop'),
    path('product-detail/<int:product_id>/', views.product, name='product-detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>', views.add_to_cart, name='add-to-cart'),
    path('decrease-item-from-cart', views.decrease_from_cart, name='decrease-item-from-cart'),
    path('delete-item-from-cart/<int:cart_item_id>', views.delete_from_cart, name='delete-item-from-cart'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/', views.show_wishlist, name='wishlist'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('save-order/', views.save_order, name='save-order'),
    path('orders/', views.orders_view, name='orders'),
    path('add-review/', views.add_review, name='add-review'),
]
