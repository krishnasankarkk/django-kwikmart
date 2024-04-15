# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
# from django_redis import get_redis_connection
import requests
import redis
import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import logout as get_out, login as get_in, authenticate
from cloudinary.models import CloudinaryResource
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from .models import Product, Carousel, Category, Cart, WishList, Order, OrderItem

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            get_in(request, user)
            messages.success(request, f'Welcome {request.user}, You are successfully logged in! ✔ ')
            next_page = request.GET.get('next', reverse('shop:home'))
            return redirect(next_page)
        else:
            messages.warning(request, 'Invalid username or password! ')
            return render(request, 'user/login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'user/login.html')
    
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sign Up successfull! ✔ ')
            return redirect('login')
    else:
        form = UserCreationForm()    
    return render(request, 'user/signup.html', {'form': form})

def logout(request):
    get_out(request)
    messages.warning(request, 'You are logged out! ')
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
    return render(request, 'pages/home.html', context)

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
    return render(request, 'pages/shop.html', context)

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
    return render(request, "pages/product-detail.html", context)

def add_to_cart(request):
    try:
        product_id = request.POST.get('product_id')
        product = Product.objects.get(pk=product_id)
        user_session = request.session.session_key
        
        if not user_session:
            request.session.save()
            user_session = request.session.session_key
            
        cart_item, created = Cart.objects.get_or_create(product=product, user_session=user_session)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            message = 'Cart updated successfully! ✔'
        else:
            message = 'Item added to cart successfully! ✔'
            
        cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
        total_price = sum(item.subtotal() for item in cart_items)
        
        # Serialize cart_items queryset into a list of dictionaries
        serialized_cart_items = []
        for item in cart_items:
            # Extracting the URL from CloudinaryResource object
            image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
            serialized_cart_items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'category': item.product.category.name,
                'image': image_url,
                'quantity': item.quantity,
                'price': item.product.price,
            })
        cart_items_count = cart_items.count()
        context = {
            'success': True, 
            'message': message, 
            'cart_items': serialized_cart_items,
            'cart_items_count': cart_items_count,
            'total_price': total_price,
        }
        return JsonResponse(context, safe=False)
    
    except Product.DoesNotExist:
        context = {
                'success': False, 
                'message': 'Product not found!', 
            }
        return JsonResponse(context, safe=False)

def decrease_from_cart(request):
    try:
        product_id = request.POST.get('product_id')
        product = Product.objects.get(pk=product_id)
        user_session = request.session.session_key
        if not user_session:
            request.session.save()
            user_session = request.session.session_key
        try:
            cart_item = Cart.objects.get(product=product, user_session=user_session)
        except Cart.DoesNotExist:
            message = 'Item not found!'
        else:
            cart_item.quantity -= 1
            cart_item.save()
            message = 'Cart updated successfully! ✔'
        
        cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
        total_price = sum(item.subtotal() for item in cart_items)
        
        # Serialize cart_items queryset into a list of dictionaries
        serialized_cart_items = []
        for item in cart_items:
            # Extracting the URL from CloudinaryResource object
            image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
            serialized_cart_items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'category': item.product.category.name,
                'image': image_url,
                'quantity': item.quantity,
                'price': item.product.price,
            })
        cart_items_count = cart_items.count()
        context = {
            'success': True, 
            'message': message, 
            'cart_items': serialized_cart_items,
            'cart_items_count': cart_items_count,
            'total_price': total_price,
        }
        return JsonResponse(context, safe=False)
    
    except Product.DoesNotExist:
        context = {
                'success': False, 
                'message': 'Product not found!', 
            }
        return JsonResponse(context, safe=False)

def delete_from_cart(request, cart_item_id):
    if request.method == 'DELETE':
        Cart.objects.get(id=cart_item_id).delete()
        user_session = request.session.session_key
        
        if not user_session:
            request.session.save()
            user_session = request.session.session_key
        
        cart_items = Cart.objects.filter(user_session=user_session)
        total_price = sum(item.subtotal() for item in cart_items)
        # Serialize cart_items queryset into a list of dictionaries
        serialized_cart_items = []
        for item in cart_items:
            # Extracting the URL from CloudinaryResource object
            image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
            serialized_cart_items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'category': item.product.category.name,
                'image': image_url,
                'quantity': item.quantity,
                'price': item.product.price,
            })
        cart_items_count = cart_items.count()
        context = {
            'deleted_item': cart_item_id,
            'cart_items': serialized_cart_items,
            'cart_items_count': cart_items_count,
            'total_price': total_price,
            'message': 'Item deleted successfully! ✔',
        }
        return JsonResponse(context, safe=False)
    else:
        return JsonResponse({'message': 'Request method is not DELETE'})
    
def cart_view(request):
    user_session = request.session.session_key
    cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
    total_price = sum(item.subtotal() for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
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
        'total_items': total_items,
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'pages/cart.html', context)

@login_required
def add_to_wishlist(request):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return HttpResponse("User does not exist", status=404)
    else:
        if request.method == 'POST':
            product_id = request.POST.get('product_id')
            if product_id:
                product = Product.objects.get(id=product_id)
                if not WishList.objects.filter(user=user, product=product).exists():
                    wishlist = WishList()
                    wishlist.user = user
                    wishlist.product = product
                    wishlist.save()
                    return JsonResponse({'success': True, 'message': 'Added to wishlist successfully! ✔'})
                else:
                    return JsonResponse({'success': False, 'message': 'Item already in wishlist!'})
            else:
                return JsonResponse({'success': False, 'message': 'Product not found!'})
        else:
            return JsonResponse({'success': False, 'message': 'Request is not POST method!'})
    
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
    return render(request, 'pages/wishlist.html', context)

def checkout_view(request):
    
    breadcrumbs = [
        {'name': 'Cart', 'url': '/cart'},
        {'name': 'Checkout', 'url': ''},
    ]
    context = {
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'pages/checkout.html', context)

def save_order(request):
    if request.method == 'POST':
        user_session = request.session.session_key
        new_order = Order(
            user_session = user_session,
            billing_name = request.POST['name'],
            billing_address = request.POST['address'],
            billing_email = request.POST['email'],
            billing_city = request.POST['city'],
            billing_postal_code = request.POST['postal_code'],
            billing_country = request.POST['country'],
            payment_method = request.POST['payment_method'],
            total_amount = float(request.POST['total_amount']),
        )
        new_order.save()
        cart_items = json.loads(request.POST.get('cart_items'))
        for item in cart_items:
            try:
                product = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                JsonResponse({'error': 'Product not Found!'})
            else:
                new_order_item = OrderItem(
                    order = new_order,
                    product = product,
                    quantity = item['quantity'],
                )
                new_order_item.save()
        Cart.objects.filter(user_session=user_session).delete()
        return JsonResponse({'message': 'Order saved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


