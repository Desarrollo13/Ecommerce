from django.shortcuts import render, redirect
from cart.cart import Cart
from .models import OrderItem
from .forms import OrderCreateForm


def order_create(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect("product_list")

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user

            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_name=item["product"].name,
                    price=item["price"],
                    quantity=item["quantity"],
                )

            cart.clear()

            return render(request, "orders/order_created.html", {
                "order": order
            })
    else:
        form = OrderCreateForm()

    return render(request, "orders/order_create.html", {
        "cart": cart,
        "form": form
    })
