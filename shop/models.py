# shop/models.py
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User

import uuid


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0, validators=[MaxValueValidator(5)])

    def __str__(self):
        return self.name

class Carousel(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField('image')

class Cart(models.Model):
    user_session = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def subtotal(self):
        return self.quantity * self.product.price

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

    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"OrderNo: {self.order.order_number} - Product: {self.product}, Quantity: {self.quantity}"

