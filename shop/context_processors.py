# context_processors.py
from cloudinary.models import CloudinaryResource

from .models import Cart, Theme, UserTheme, SessionTheme

def theme(request):
    try:
        themes = Theme.objects.all()
    except Theme.DoesNotExist:
        raise ValueError("Themes does not exists!")
    else:
        user = request.user if request.user.is_authenticated else None
        try:
            user_theme = UserTheme.objects.get(user=user)
        except UserTheme.DoesNotExist:
            user_session = request.session.session_key
            if not user_session:
                request.session.save()
                user_session = request.session.session_key
            try:
                session_theme = SessionTheme.objects.get(user_session=user_session)
            except SessionTheme.DoesNotExist:
                selected_theme = Theme.objects.get(selected=True)
                return {'selected_theme':selected_theme, 'themes':themes}
            else:
                return {'selected_theme':session_theme.theme, 'themes':themes}
        else:
            return {'selected_theme':user_theme.theme, 'themes':themes}
                


def cart_items(request):
    user_session = request.session.session_key
    if not user_session:
        request.session.save()
        user_session = request.session.session_key
    user = request.user if request.user.is_authenticated else None
    if user:
        cart_items = Cart.objects.filter(user=user).order_by('created_at')
    else:
        cart_items = Cart.objects.filter(user_session=user_session).order_by('created_at')
    if cart_items:
        cart_item_count = cart_items.count()
        total_price = sum(item.sub_total for item in cart_items)
        total_original_price = sum(item.product.original_price*item.quantity for item in cart_items)
        total_discount_price = total_original_price - total_price
        total_discount = total_discount_price/total_original_price*100
        total_price_afer_discount = total_original_price - total_discount_price + 40
        
        serialized_cart_items = []
        for item in cart_items:
            # Extracting the URL from CloudinaryResource object
            image_url = item.product.image.url if isinstance(item.product.image, CloudinaryResource) else None
            serialized_cart_items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'original_price': item.product.original_price,
                'offer_price': item.product.offer_price,
                'discount': item.product.discount,
                'category': item.product.category.name,
                'image': image_url,
                'quantity': item.quantity,
                'sub_total': item.sub_total,
                'total_mrp': item.product.original_price*item.quantity,
            })
        
        context = {
            'items_in_cart': cart_items,
            'cart_items': serialized_cart_items,
            'cart_item_count': cart_item_count,
            'total_price': total_original_price,
            'total_offer_price': total_price_afer_discount,
            'total_discount':round(total_discount, 2),
            'total_discount_price':total_discount_price,
        }
        return context
    else:
        return {'cart_item_count': 0,'total_offer_price':0}
        

def breadcrumbs(request):
    
    breadcrumbs = [
        {'name': 'Products', 'url': '/products/'},
        {'name': 'Category', 'url': '/products/category/'},
        {'name': 'Current Page', 'url': request.path},  # Example: Current page
    ]
    return {'breadcrumbs': breadcrumbs}

