# shop/urls.py
from django.urls import path
from django.contrib.sitemaps.views import sitemap

from shop.sitemaps import ProductSitemap
from shop import views

sitemaps = {
    'products': ProductSitemap,
}

app_name = 'shop'

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps':sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', views.home, name='home'),
    path('shop', views.shop, name='shop'),
    path('filtered-shop/<str:categories>/', views.filtered_shop, name='filtered-shop'),
    path('filtered-shop/<str:categories>/<str:brands>', views.filtered_shop, name='filtered-shop'),
    path('product-detail/<int:product_id>/', views.product, name='product-detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('decrease-item-from-cart', views.decrease_from_cart, name='decrease-item-from-cart'),
    path('delete-item-from-cart/<int:cart_item_id>', views.delete_from_cart, name='delete-item-from-cart'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add-to-wishlist'),
    path('delete-item-from-wishlist/<int:product_id>/', views.delete_from_wishlist, name='delete-item-from-wishlist'),
    path('wishlist/', views.show_wishlist, name='wishlist'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('save-order/', views.save_order, name='save-order'),
    path('orders/', views.orders_view, name='orders'),
    path('add-review/', views.add_review, name='add-review'),
    path('filter-products/', views.filter_products, name='filter-products'),
    path('change-theme/<int:theme_id>', views.change_theme, name='change-theme'),
    path('search-product/<str:search>', views.search_product, name='search-product'),
    path('search-category-product/<int:category_id>/<str:search>', views.search_category_product, name='search-category-product'),
    path('update-account/', views.update_account, name="update-account")
]
