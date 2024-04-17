# shop/models.py
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User

import uuid, math


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.IntegerField(default=0)
    image = CloudinaryField('image')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0, validators=[MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.offer_price > 0 and self.discount <= 0:
            # Calculate discount if offer_price is provided without discount
            self.discount = self._calculate_discount()
        elif self.discount > 0 and self.offer_price <= 0:
            # Calculate offer_price if discount is provided without offer_price
            self.offer_price = self._calculate_offer_price()
        elif self.offer_price <= 0 and self.discount > 0 :
            # Validate and adjust offer_price and discount if both are provided
            calculated_offer_price = self._calculate_offer_price()
            if calculated_offer_price != self.offer_price:
                # If calculated offer_price is different, recalculate discount
                self.discount = self._calculate_discount()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
            
    def _calculate_discount(self):
        if self.original_price != 0:
            return int(((self.original_price - self.offer_price) / self.original_price) * 100)
        else:
            return 0

    def _calculate_offer_price(self):
        return math.ceil(float(float(self.original_price) * (1 - (float(self.discount) / 100)))/100)*100


class Carousel(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user_session = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def subtotal(self):
        return self.quantity * self.product._get_offer_price()

class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product} added to wishlist by {self.user}'
    
    def save(self, *args, **kwargs):
        # Check if an entry with the same user and product already exists
        existing_entry = WishList.objects.filter(user=self.user, product=self.product).exists()
        
        if existing_entry:
            # Optionally, you can raise an exception, ignore the save operation, or handle it in another way
            raise ValueError("This product is already in the wishlist.")
        
        # If no existing entry found, proceed with saving
        super().save(*args, **kwargs)

class Order(models.Model):
    user_session = models.CharField(max_length=100)
    billing_name = models.CharField(max_length=255)
    billing_address = models.TextField()
    billing_email = models.EmailField()
    billing_city = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50)
    order_number = models.CharField(max_length=20, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status_choices = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def _generate_order_number(self):
        prefix = 'KM-ORDER'
        last_order = Order.objects.order_by('-id').first()
        last_order_number = last_order.id if last_order else 0
        new_order_number = (last_order_number) + 1
        return f'{prefix}:{str(new_order_number).zfill(6)}'
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.quantity * self.product._get_offer_price()

    def __str__(self):
        return f"OrderNo: {self.order.order_number} - Product: {self.product}, Quantity: {self.quantity}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
