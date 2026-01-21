from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Order


@receiver(post_save, sender=Order)
def send_order_paid_email(sender, instance, created, **kwargs):
    """
    Envia email SOLO cuando la orden pasa a PAID
    """

    if created:
        return  # no enviar al crear

    if instance.status == "paid":
        subject = f"✅ Pago confirmado - Orden #{instance.id}"
        message = f"""
Hola {instance.first_name},

¡Gracias por tu compra!

Tu pago fue confirmado correctamente.
Número de orden: #{instance.id}
Total: ${instance.get_total()}

Pronto nos pondremos en contacto para el envío.

Saludos,
Ecommerce
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True,
        )
