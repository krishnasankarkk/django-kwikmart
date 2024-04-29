# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
# from django_redis import get_redis_connection
from datetime import datetime, timedelta
import redis
import json
from cloudinary.models import CloudinaryResource
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import logout as get_out, login as get_in, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET, require_http_methods
from django.db.models import Q, Sum, F, Case, When, IntegerField, CharField, DateTimeField
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Product, Carousel, Category, Cart, WishList, Order, OrderItem, Review, Brand, Theme, UserTheme, SessionTheme, Account

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
            messages.success(request, 'Successfully created account! ✔ ')
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
    best_deals = Product.objects.filter(discount__gt=0).order_by('-discount')[:20]
    best_deal = best_deals.first()
    threshold_date = timezone.now() - timedelta(days=7)
    new_products = products.filter(created_at__gte=threshold_date)
    context = {
        'carousel': carousel,
        'categories': categories,
        'products': products,
        'best_deals': best_deals,
        'best_deal': best_deal,
        'new_products': new_products,
    }
    return render(request, 'pages/home.html', context)

def shop(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    brands = Brand.objects.all()
    threshold_date = datetime.now() - timedelta(days=7)
    breadcrumbs = [
        {'name': 'Shop', 'url': ''},  # Example: Current page
    ]
    context = {
        'categories': categories,
        'products': products,
        'brands': brands,
        'breadcrumbs':breadcrumbs,
        'is_new': datetime.now()>threshold_date,
    }
    return render(request, 'pages/shop.html', context)

def product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    reviews = Review.objects.filter(product_id=product_id)
    breadcrumbs = [
        {'name': 'Shop', 'url': '/shop'},
        {'name': 'Product', 'url': ''},
    ]
    context = {
        'product': product,
        'categories': categories,
        'breadcrumbs': breadcrumbs,
        'reviews': reviews,
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
        
        user = request.user if request.user.is_authenticated else None

        if user:
            cart_item, created = Cart.objects.get_or_create(product=product, user=user)
        else:
            cart_item, created = Cart.objects.get_or_create(product=product, user_session=user_session)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            message = 'Cart updated successfully! ✔'
        else:
            message = 'Item added to cart successfully! ✔'
        
        if user:    
            cart_items = Cart.objects.filter(user=user).order_by('created_at')
        else:
            cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
        total_price = sum(item.sub_total for item in cart_items)
        
        # Serialize cart_items queryset into a list of dictionaries
        serialized_cart_items = []
        for item in cart_items:
            # Extracting the URL from CloudinaryResource object
            image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
            serialized_cart_items = [
                {
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name[:39]+'...',
                    'original_price': item.product.original_price,
                    'offer_price': item.product.offer_price,
                    'discount': item.product.discount,
                    'category': item.product.category.name,
                    'image': item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None,
                    'quantity': item.quantity,
                    'sub_total': item.sub_total,
                }
                for item in cart_items
            ]

        cart_items_count = cart_items.count()
        context = {
            'success': True, 
            'message': message, 
            'cart_items': serialized_cart_items,
            'cart_items_count': cart_items_count,
            'total_price': total_price,
        }
        messages.success(request, message)
        return JsonResponse(context)
    except Product.DoesNotExist:
        context = {
                'success': False, 
                'message': 'Product not found!', 
            }
        return JsonResponse(context)

def decrease_from_cart(request):
    try:
        product_id = request.POST.get('product_id')
        product = Product.objects.get(pk=product_id)
        user_session = request.session.session_key
            
        if not user_session:
            request.session.save()
            user_session = request.session.session_key
        user = request.user if request.user.is_authenticated else None
        if user:
            cart_item = Cart.objects.get(product=product, user=user)
        else:
            cart_item = Cart.objects.get(product=product, user_session=user_session)
        if cart_item:
            cart_item.quantity -= 1
            cart_item.save()
            message = 'Cart updated successfully! ✔'
        if user:
            cart_items = Cart.objects.filter(user=user).order_by('created_at')
        else:
            cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
        total_price = sum(item.sub_total for item in cart_items)
        
        # Serialize cart_items queryset into a list of dictionaries
        serialized_cart_items = []
        for item in cart_items:
            # Extracting the URL from CloudinaryResource object
            image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
            serialized_cart_items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name[:40] + ('...' if len(item.product.name) > 40 else ''),
                'original_price': item.product.original_price,
                'offer_price': item.product.offer_price,
                'discount': item.product.discount,
                'category': item.product.category.name,
                'image': image_url,
                'quantity': item.quantity,
                'sub_total': item.sub_total,

            })
        cart_items_count = cart_items.count()
        context = {
            'success': True, 
            'message': message, 
            'cart_items': serialized_cart_items,
            'cart_items_count': cart_items_count,
            'total_price': total_price,
        }
        messages.success(request, 'Cart updated successfully! ✔')
        return JsonResponse(context, safe=False)
    
    except Product.DoesNotExist:
        context = {
                'success': False, 
                'message': 'Product not found!', 
            }
        return JsonResponse(context, safe=False)

def delete_from_cart(request, cart_item_id):
    if request.method == 'DELETE':
        try:
            Cart.objects.get(id=cart_item_id).delete()
        except Cart.DoesNotExist:
            return JsonResponse({'success':False, 'message': 'Cart not found'})
        else:
            user_session = request.session.session_key
            
            if not user_session:
                request.session.save()
                user_session = request.session.session_key
            user = request.user if request.user.is_authenticated else None
            if user:
                cart_items = Cart.objects.filter(user=user)
            else:
                cart_items = Cart.objects.filter(user_session=user_session)
            total_price = sum(item.sub_total for item in cart_items)
            # Serialize cart_items queryset into a list of dictionaries
            serialized_cart_items = []
            for item in cart_items:
                # Extracting the URL from CloudinaryResource object
                image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
                serialized_cart_items.append({
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name[:40] + ('...' if len(item.product.name) > 40 else ''),
                    'original_price': item.product.original_price,
                    'offer_price': item.product.offer_price,
                    'discount': item.product.discount,
                    'category': item.product.category.name,
                    'image': image_url,
                    'quantity': item.quantity,
                    'sub_total': item.sub_total,

                })
            cart_items_count = cart_items.count()
            context = {
                'deleted_item': cart_item_id,
                'cart_items': serialized_cart_items,
                'cart_items_count': cart_items_count,
                'total_price': total_price,
                'message': 'Item deleted successfully! ✔',
            }
            messages.success(request, 'Item deleted successfully! ✔')
            return JsonResponse(context, safe=False)
    else:
        return JsonResponse({'message': 'Request method is not DELETE'})
    
def cart_view(request):
    breadcrumbs = [
        {'name': 'Shop', 'url': '/shop'},
        {'name': 'Cart', 'url': ''},
    ]
    context = {
        'breadcrumbs':breadcrumbs,
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

@require_http_methods(["DELETE"])
def delete_from_wishlist(request, product_id):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return HttpResponse("User does not exist", status=404)
    else:
        if product_id:
            product = Product.objects.get(id=product_id)
            wishlist_item = WishList.objects.filter(user=user, product=product)
            if wishlist_item.exists():
                wishlist_item.delete()
                messages.success(request, 'Successfully removed item from wishlist! ✔')
                return JsonResponse({'success': True, 'message': 'Successfully removed item from wishlist! ✔'})
            else:
                return JsonResponse({'success': False, 'message': 'Item is not in wishlist!'})
        else:
            return JsonResponse({'success': False, 'message': 'Product not found!'})

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
        {'name': 'Shop', 'url': '/shop'},
        {'name': 'Cart', 'url': '/cart'},
        {'name': 'Checkout', 'url': ''},
    ]
    context = {
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'pages/checkout.html', context)

@require_http_methods(["POST"])
def save_order(request):
    user_session = request.session.session_key
    user = request.user if request.user.is_authenticated else None
    new_order = Order(
        user = user,
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
    if user:
        Cart.objects.filter(user=user).delete()
    else:
        Cart.objects.filter(user_session=user_session).delete()
    # messages.success(request, 'Order saved successfully')
    return JsonResponse({'success': True, 'message': f'Order placed successfully! Order No : {new_order.order_number} ✔'})

@login_required
@require_http_methods(["POST"])
def add_review(request):
    user = request.user if request.user.is_authenticated else None
    if not user:
        return JsonResponse({'success': False, 'message': 'Authentication required!'}, status=401)

    try:
        product = Product.objects.get(id=request.POST.get('product_id'))
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found!'}, status=404)
    
    rating = request.POST.get('rating')
    comment = request.POST.get('comment')
    
    if not rating:
        return JsonResponse({'success': False, 'message': 'Rating are required!'}, status=400)
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValidationError('Rating must be between 1 and 5')
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid rating!'}, status=400)
    
    new_review = Review(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
    )
    new_review.save()
    product._update_rating()
    
    serialized_review = {
        'rating': new_review.rating,
        'comment': new_review.comment,
    }    
    
    context = {
        'success': True, 
        'message': 'Review submitted successfully!', 
        'review': serialized_review, 
        'rating': product.rating,
        }
    return JsonResponse(context)
        
@login_required
def orders_view(request):
    user = request.user if request.user.is_authenticated else None
    if user:
        orders = (
            OrderItem.objects.filter(order__user=user)
                .annotate(orderid=F('order__id'))
                .values('orderid')
                .annotate(
                    total_quantity=Sum('quantity'),
                    order_number=Case(
                        When(order__id=F('orderid'), then=F('order__order_number')),
                        output_field=CharField(),
                    ),
                    order_date=Case(
                        When(order__id=F('orderid'), then=F('order__order_date')),
                        output_field=DateTimeField(),
                    ),
                    billing_name=Case(
                        When(order__id=F('orderid'), then=F('order__billing_name')),
                        output_field=CharField(),
                    ),
                    total_amount=Case(
                        When(order__id=F('orderid'), then=F('order__total_amount')),
                        output_field=IntegerField(),
                    ),
                    status=Case(
                        When(order__id=F('orderid'), then=F('order__status')),
                        output_field=CharField(),
                    ),
                    payment_method=Case(
                        When(order__id=F('orderid'), then=F('order__payment_method')),
                        output_field=CharField(),
                    ),
                    payment_status=Case(
                        When(order__id=F('orderid'), then=F('order__payment_status')),
                        output_field=CharField(),
                    ),
                )
                .order_by('orderid')
            )

    breadcrumbs = [
        {'name': 'Shop', 'url': '/shop'},
        {'name': 'Orders', 'url': ''},
    ]
    context = {
        'orders': orders,
        'breadcrumbs': breadcrumbs,
    }
    return render(request, 'pages/orders.html', context)

@require_GET
def filter_products(request):
    categories = request.GET.get('categories', '[]')
    categories = json.loads(categories)
    categories = [int(item) for item in categories]
    
    prices = request.GET.get('prices', '[]')
    prices = json.loads(prices)
    prices = [int(item) for item in prices]
    
    brands = request.GET.get('brands', '[]')
    brands = json.loads(brands)
    brands = [int(item) for item in brands]
    
    ratings = request.GET.get('ratings', '[]')
    ratings = json.loads(ratings)
    ratings = [int(item) for item in ratings]
    
    offers = request.GET.get('offers', '[]')
    offers = json.loads(offers)
    offers = [int(item) for item in offers]
    
     # Filtering products based on multiple criteria
    products = Product.objects.all()
    if categories:
        products = products.filter(category__id__in=categories)
    if prices:
        price_filters = Q()
        for price in prices:
            if price == 1:
                price_filters |= Q(offer_price__lt=1000)
            elif price == 8:
                price_filters |= Q(offer_price__gt=50000)
            else:        
                ranges = {
                    2: (1000, 5000),
                    3: (5000, 10000),
                    4: (10000, 20000),
                    5: (20000, 30000),
                    6: (30000, 40000),
                    7: (40000, 50000),
                }
                if price:
                    price_filters |= Q(offer_price__range=ranges[price])
        products = products.filter(price_filters)
    if brands:
        # Assuming brand is a field in the Product model
        products = products.filter(brand__id__in=brands)
    if ratings:
        # Assuming rating is a field in the Product model
        products = products.filter(rating__in=ratings)
    if offers:
        for offer_value in offers:
            products = products.filter(discount__gte=offer_value)
    # You can add additional context if needed
    context = {
        'products': [
            {
                'id': product.id,
                'name': product.name[:40] + ('...' if len(product.name) > 40 else ''),
                'original_price': product.original_price,
                'offer_price': product.offer_price,
                'discount': product.discount,
                'category': product.category.name,
                'brand': product.brand.name,
                'rating': product.rating,
                # Extract the image URL from the Cloudinary field
                'image_url': product.image.url if product.image else None,
                # Other fields of the product model
            }
            for product in products if products
        ],
        'success' : True,
        'message' : "Products updated! ✔",
    }

    return JsonResponse(context, safe=False)

def change_theme(request, theme_id):
    user = request.user if request.user.is_authenticated else None
    try:
        theme = Theme.objects.get(id=theme_id)
    except Theme.DoesNotExist:
        return JsonResponse({'message':'Theme does not exists!'})
    else:
        try:
            user_theme = UserTheme.objects.get(user=user)
        except UserTheme.DoesNotExist:
            if user:
                new_user_theme = UserTheme(
                    user=user,
                    theme=theme,
                )
                new_user_theme.save()
            else:
                user_session = request.session.session_key
                if not user_session:
                    request.session.save()
                    user_session = request.session.session_key
                try:
                    session_theme = SessionTheme.objects.get(user_session=user_session)
                except SessionTheme.DoesNotExist:
                    new_session_theme = SessionTheme(
                        user_session = user_session,
                        theme = theme,
                    )
                    new_session_theme.save()
                else:
                    session_theme.theme = theme
                    session_theme.save()
        else:
            user_theme.theme = theme
            user_theme.save()
        
    previous_url = request.META.get('HTTP_REFERER', None)
    return redirect(previous_url)

@require_GET
def search_product(request, search):
    products = Product.objects.filter(name__icontains=search)
    context = {
        'products': [
            {
                'id': product.id,
                'name': product.name[:50]+'...',
                'brand': product.brand.name,
            }
            for product in products
        ],
    }
    return JsonResponse(context)

def account_view(request):
    return render(request, 'pages/account.html')

@require_http_methods(["POST"])
def update_account(request):
    if request.user.is_authenticated:
        user = request.user
        username = request.POST.get('username')
        fullname = request.POST.get('fullname')
        old_password = request.POST.get('old-password')
        new_password = request.POST.get('new-password')
        primary_billing_address = request.POST.get('address')

        # Update username if provided
        if username:
            user.username = username

        # Update fullname if provided
        if fullname:
            user.first_name, user.last_name = fullname.split(maxsplit=1)

        # Check if old password matches and new password is provided
        if old_password and new_password:
            if user.check_password(old_password):
                user.set_password(new_password)
            else:
                return JsonResponse({'error': 'Old password is incorrect.'}, status=400)

        # Update primary billing address if provided
        if primary_billing_address:
            try:
                account = Account.objects.get(user=user)
            except Account.DoesNotExist:
                return JsonResponse({'error': 'Account does not exist.'}, status=404)
            else:
                if 'image' in request.FILES:
                    account.image = request.FILES['change-image']
                if 'billing_address1' in request.POST:
                    account.billing_address1 = primary_billing_address
                account.save()

        # Save the user object
        user.save()

        return JsonResponse({'message': 'Account updated successfully.'})
    else:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)