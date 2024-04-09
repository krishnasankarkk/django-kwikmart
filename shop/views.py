# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
# from django_redis import get_redis_connection
import redis
import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import logout as get_out, login as get_in, authenticate
from cloudinary.models import CloudinaryResource
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from .models import Product, Carousel, Category, Cart, WishList

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            get_in(request, user)
            messages.success(request, 'Login successfull! ✔ ')
            return redirect('shop:home')
        else:
            messages.warning(request, 'Invalid username or password! ')
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')
    
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sign Up successfull! ✔ ')
            return redirect('login')
    else:
        form = UserCreationForm()    
    return render(request, 'signup.html', {'form': form})

def logout(request):
    get_out(request)
    return redirect('login')

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

def shop(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    breadcrumbs = [
        {'name': 'Shop', 'url': ''},  # Example: Current page
    ]
    context = {
        'categories': categories,
        'products': products,
        'breadcrumbs':breadcrumbs,
    }
    return render(request, 'shop.html', context)

def product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    breadcrumbs = [
        {'name': 'Shop', 'url': '/shop'},
        {'name': 'Product Details', 'url': ''},
    ]
    context = {
        'product': product,
        'categories': categories,
        'breadcrumbs':breadcrumbs,
    }
    return render(request, "product-detail.html", context)

def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    user_session = request.session.session_key
    if not user_session:
        request.session.save()
        user_session = request.session.session_key
    cart_item, created = Cart.objects.get_or_create(product=product, user_session=user_session)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, 'Cart updated! ✔')
    else:
        messages.success(request, 'Added to cart successfully! ✔ ')
    # Get the referring URL
    referring_url = request.META.get('HTTP_REFERER')
    # print(referring_url)
    #  # Check if the referring URL is the product detail page
    # if referring_url and referring_url.contains('/product-detail/'):
    #     # Redirect to the product detail page
    #     return redirect(referring_url)
    # else:
    #     # Redirect to the cart page
    #     return redirect(reverse('cart_page_name'))
    # return redirect(reverse('shop:product-detail', kwargs={'product_id': product_id}))
    return redirect(referring_url)

def delete_from_cart(request, product_id):
    item_to_delete = Cart.objects.filter(product_id=product_id)
    item_to_delete.delete()
    messages.success(request, 'Item deleted successfully! ✔')
    return redirect('shop:cart')

def get_session_cart_items(request):
    user_session = request.session.session_key
    cart_item_count = Cart.objects.filter(user_session=user_session).order_by('created_at').count()
    context = {
        'cart_item_count' : cart_item_count,
    }
    return JsonResponse(context, safe=False)
    
def get_cart_data(request):
    user_session = request.session.session_key
    cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    # Serialize cart_items queryset into a list of dictionaries
    serialized_cart_items = []
    for item in cart_items:
        # Extracting the URL from CloudinaryResource object
        image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
        serialized_cart_items.append({
            'product_id': item.product.id,
            'product_name': item.product.name,
            'category': item.product.category,
            'image': image_url,
            'quantity': item.quantity,
            'price': item.product.price,
        })
    breadcrumbs = [
        {'name': 'Cart', 'url': ''},
    ]
    context = {
        'cart_items': serialized_cart_items,
        'total_price': total_price,
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'cart.html', context)

@login_required
def add_to_wishlist(request, product_id):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return HttpResponse("User does not exist", status=404)
    else:
        product = Product.objects.get(id=product_id)
        if not WishList.objects.filter(user=user, product=product).exists():
            wishlist = WishList()
            wishlist.user = user
            wishlist.product = product
            wishlist.save()
            messages.success(request, 'Added to wishlist successfully! ✔')
        else:
            messages.warning(request, 'Item already in wishlist!')
        return redirect(reverse('shop:product-detail', kwargs={'product_id': product_id}))
    
@login_required
def show_wishlist(request):
    wishlist = WishList.objects.all()
    items_count = wishlist.count()
    breadcrumbs = [
        {'name': 'Wishlist', 'url': ''},
    ]
    context = {
        'wishlist': wishlist,
        'items_count': items_count,
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'wishlist.html', context)