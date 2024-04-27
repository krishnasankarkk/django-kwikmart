# admin.py

from django.contrib import admin
from . import models

admin.site.register(models.Category)
admin.site.register(models.Product)
admin.site.register(models.Carousel)
admin.site.register(models.Cart)
admin.site.register(models.WishList)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)
admin.site.register(models.Brand)
admin.site.register(models.Review)
admin.site.register(models.Theme)
admin.site.register(models.UserTheme)
admin.site.register(models.SessionTheme)
admin.site.register(models.Account)
