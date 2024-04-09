# admin.py

from django.contrib import admin
from .models import Category, Product, Carousel, Cart, WishList

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Carousel)
admin.site.register(Cart)
admin.site.register(WishList)
