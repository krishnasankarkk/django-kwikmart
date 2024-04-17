# context_processors.py

from .models import Cart

def cart_item_count(request):
    user_session = request.session.session_key
    cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
    cart_item_count = cart_items.count()
    total_price = sum(item.subtotal() for item in cart_items)
    updated_cart_items = []
    for item in cart_items:
        offer_price = item.product._get_offer_price()
        data = {
            'cart_item': item,
            'price': offer_price,
        }
        updated_cart_items.append(data)
    context = {
        'items_in_cart': updated_cart_items,
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

