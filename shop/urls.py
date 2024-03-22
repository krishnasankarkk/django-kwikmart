# shop/urls.py
from django.urls import path

from shop.views import index


urlpatterns = [
    path('', index),
]