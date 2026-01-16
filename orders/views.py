import mercadopago
from django.conf import settings
from django.shortcuts import render, redirect,get_object_or_404
from cart.cart import Cart
from .models import OrderItem,Order
from .forms import OrderCreateForm
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt


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




def create_mp_preference(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    sdk = mercadopago.SDK(
        "APP_USR-1525879268983887-011517-d6aa76ac6d53ef3cd6d536ca9905eb1b-3136918293"
    )

    
    preference_data = {
    "items": [
        {
            "title": f"Orden #{order.id}",
            "quantity": 1,
            "unit_price": float(order.get_total()),
            "currency_id": "ARS",
        }
    ],
    
    "back_urls": {
    "success": request.build_absolute_uri("/orden/pagos/exito/"),
    "failure": request.build_absolute_uri("/orden/pagos/error/"),
    "pending": request.build_absolute_uri("/orden/pagos/pendiente/"),   
    },
    "notification_url": request.build_absolute_uri(
        "/orden/pagos/webhook/"
    ),





    # "auto_return": "approved",
    "external_reference": str(order.id),

}


    preference = sdk.preference().create(preference_data)

    print("RESPUESTA MERCADO PAGO:", preference)

    response = preference.get("response")

    if not response:
        return HttpResponse("❌ Error: respuesta vacía de Mercado Pago")

    init_point = response.get("sandbox_init_point") or response.get("init_point")

    if not init_point:
        return HttpResponse(
            f"❌ Error al crear preferencia<br><pre>{preference}</pre>"
        )

    return redirect(init_point)





def pago_exito(request):
    payment_id = request.GET.get("payment_id")
    external_reference = request.GET.get("external_reference")

    if not payment_id or not external_reference:
        return HttpResponse("Pago inválido", status=400)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    payment = sdk.payment().get(payment_id)

    response = payment.get("response", {})

    if response.get("status") == "approved":
        order = get_object_or_404(Order, id=external_reference)

        order.status = "paid"
        order.save()

        return render(
            request,
            "orders/pago_exito.html",
            {"order": order}
        )

    return HttpResponse("El pago no fue aprobado", status=400)



def pago_error(request):
    return HttpResponse("Pago rechazado ❌")


def pago_pendiente(request):
    return HttpResponse("Pago pendiente ⏳")







@csrf_exempt
def mercadopago_webhook(request):
    data = json.loads(request.body)

    payment_id = data.get("data", {}).get("id")
    topic = data.get("type")

    if topic == "payment":
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        payment = sdk.payment().get(payment_id)

        payment_data = payment["response"]

        if payment_data["status"] == "approved":
            order_id = payment_data["external_reference"]

            order = Order.objects.get(id=order_id)
            order.status = "paid"
            order.mercadopago_payment_id = payment_id
            order.save()

    return HttpResponse(status=200)
