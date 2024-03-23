# shop/views.py
from django.shortcuts import render, redirect
from .models import Product, Carousel, Category

def home(request):
    carousel = Carousel.objects.all()
    categories = Category.objects.all()
    products = Product.objects.all()
    context = {
        'carousel': carousel,
        'categories': categories,
        'products': products,
    }
    return render(request, 'home.html', context)


def index(request):
    return render(request, 'home.html')