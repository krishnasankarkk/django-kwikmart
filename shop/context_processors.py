# context_processors.py

from .models import Cart

def cart_item_count(request):
    user_session = request.session.session_key
    cart_item_count = Cart.objects.filter(user_session=user_session).order_by('created_at').count()
    return {'cart_item_count': cart_item_count}

def breadcrumbs(request):
    
    breadcrumbs = [
        {'name': 'Products', 'url': '/products/'},
        {'name': 'Category', 'url': '/products/category/'},
        {'name': 'Current Page', 'url': request.path},  # Example: Current page
    ]
    return {'breadcrumbs': breadcrumbs}

