from django.shortcuts import render

## impoer the generic view
from django.views.generic import ListView,DetailView
from .models import Product

## need mixins for authentication guard
from django.contrib.auth.mixins import LoginRequiredMixin

## see the list without login

class Home(ListView):
    model = Product
    template_name = "App_Shop/home.html"

## detail view required login

class ProductDetail(LoginRequiredMixin,DetailView):
    model = Product
    template_name = "App_Shop/product_detail.html"