# shop/models.py
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User


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

