from django.urls import path

from .import views


app_name = "orders"

urlpatterns = [
    path("crear/", views.order_create, name="order_create"),
    path("pagar/<int:order_id>/", views.create_mp_preference, name="mp_pagar"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    
    path("pago/exito/<int:order_id>/", views.pago_exito, name="pago_exito"),
    path("pagos/error/", views.pago_error, name="pago_error"),
    path("pagos/pendiente/", views.pago_pendiente, name="pago_pendiente"),
    # mercadopago
    path("pagos/webhook/", views.mercadopago_webhook, name="mp_webhook"),

    path("mis-compras/", views.mis_compras, name="mis_compras"),
    path("factura/<int:order_id>/", views.factura_pdf, name="factura_pdf"),



    





    

]
