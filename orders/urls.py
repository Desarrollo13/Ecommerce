from django.urls import path

from .import views


app_name = "orders"

urlpatterns = [
    path("crear/", views.order_create, name="order_create"),
    path("pagar/<int:order_id>/", views.create_mp_preference, name="mp_pagar"),
    
    path("pagos/exito/", views.pago_exito, name="pago_exito"),
    path("pagos/error/", views.pago_error, name="pago_error"),
    path("pagos/pendiente/", views.pago_pendiente, name="pago_pendiente"),
    # mercadopago
    path("pagos/webhook/", views.mercadopago_webhook, name="mp_webhook"),

]
