from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'order_number', ]