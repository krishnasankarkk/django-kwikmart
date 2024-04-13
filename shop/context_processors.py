# context_processors.py

from .models import Cart

def cart_item_count(request):
    user_session = request.session.session_key
    cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
    cart_item_count = cart_items.count()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    context = {
        'items_in_cart': cart_items,
        'cart_item_count': cart_item_count,
        'total_price': total_price,
    }
    return context

def breadcrumbs(request):
    
    breadcrumbs = [
        {'name': 'Products', 'url': '/products/'},
        {'name': 'Category', 'url': '/products/category/'},
        {'name': 'Current Page', 'url': request.path},  # Example: Current page
    ]
    return {'breadcrumbs': breadcrumbs}

