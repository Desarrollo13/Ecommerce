from django.shortcuts import render
from products.models import Product

# Create your views here.
def home_view(request):
    featured_products = Product.objects.filter(is_featured=True)[:8]
    return render(request, "core/home.html", {
        "featured_products": featured_products
    })