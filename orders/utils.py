from django.core.mail import send_mail
from django.conf import settings


def send_payment_success_email(order):
    subject = f"Pago confirmado - Orden #{order.id}"

    message = f"""
Hola {order.first_name},

¡Gracias por tu compra! 🎉

📦 Orden Nº: {order.id}
💰 Total pagado: $ {order.get_total()}
📅 Fecha: {order.created_at.strftime('%d/%m/%Y %H:%M')}

Podés ver el detalle de tu orden acá:
http://127.0.0.1:8000/orden/{order.id}/

Saludos,
MiEcommerce
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )
