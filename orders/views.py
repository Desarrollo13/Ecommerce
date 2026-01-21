import mercadopago
from django.conf import settings
from django.shortcuts import render, redirect,get_object_or_404
from cart.cart import Cart
from .models import OrderItem,Order
from .forms import OrderCreateForm
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .utils import send_payment_success_email
from django.template.loader import get_template
from xhtml2pdf import pisa



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




@login_required
def order_detail(request, order_id):

    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

    return render(
        request,
        "orders/order_detail.html",
        {"order": order}
    )







def create_mp_preference(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


    
    
    NGROK_URL = "https://limbless-untaciturn-ardith.ngrok-free.dev"

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
        "success": f"{NGROK_URL}/orden/pagos/exito/",
        "failure": f"{NGROK_URL}/orden/pagos/error/",
        "pending": f"{NGROK_URL}/orden/pagos/pendiente/",
    },
    "notification_url": f"{NGROK_URL}/orden/pagos/webhook/",
    "external_reference": str(order.id),
    "binary_mode": True,
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








def pago_exito(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != "paid":
        return render(
            request,
            "orders/pago_invalido.html",
            {"order": order}
        )

    # 🔔 ENVIAR EMAIL SOLO UNA VEZ
    if not order.mp_payment_id:
        send_payment_success_email(order)
        order.mp_payment_id = "email_sent"
        order.save()

    return render(
        request,
        "orders/pago_exito.html",
        {"order": order}
    )




def pago_error(request):
    return HttpResponse("Pago rechazado ❌")


def pago_pendiente(request):
    return HttpResponse("Pago pendiente ⏳")



@csrf_exempt
def mercadopago_webhook(request):
    try:
        topic = request.GET.get("topic")
        resource_id = request.GET.get("id")

        print("📩 WEBHOOK:", topic, resource_id)

        if not topic or not resource_id:
            print("⚠️ Webhook incompleto")
            return HttpResponse(status=200)

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        if topic != "merchant_order":
            print("ℹ️ Topic ignorado:", topic)
            return HttpResponse(status=200)

        mo_result = sdk.merchant_order().get(resource_id)
        merchant_order = mo_result.get("response")

        if not merchant_order:
            print("❌ merchant_order vacío:", mo_result)
            return HttpResponse(status=200)

        print("📦 MERCHANT ORDER:", merchant_order)

        order_id = merchant_order.get("external_reference")
        if not order_id:
            print("❌ Sin external_reference")
            return HttpResponse(status=200)

        payments = merchant_order.get("payments", [])
        if not payments:
            print("⚠️ Sin pagos todavía")
            return HttpResponse(status=200)

        for p in payments:
            payment_id = p.get("id")
            if not payment_id:
                continue

            payment_info = sdk.payment().get(payment_id)
            payment_data = payment_info.get("response", {})

            print("💳 PAYMENT:", payment_id, payment_data.get("status"))

            if payment_data.get("status") == "approved":
                order = Order.objects.filter(id=order_id).first()
                if not order:
                    print("❌ Orden no encontrada:", order_id)
                    return HttpResponse(status=200)

                order.status = "paid"
                order.save()
                print(f"✅ ORDEN {order_id} MARCADA COMO PAGADA")
                break

        return HttpResponse(status=200)

    except Exception as e:
        print("🔥 ERROR WEBHOOK:", str(e))
        return HttpResponse(status=200)





@login_required
def mis_compras(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/mis_compras.html",
        {"orders": orders}
    )

@login_required
def factura_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Seguridad
    if not request.user.is_staff and order.user != request.user:
        return HttpResponse("No autorizado", status=403)

    template = get_template("orders/factura_pdf.html")
    html = template.render({"order": order})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="factura_orden_{order.id}.pdf"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response
    )

    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=500)

    return response