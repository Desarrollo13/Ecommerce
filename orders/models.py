from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("paid", "Pagado"),
        ("shipped", "Enviado"),
        ("cancelled", "Cancelado"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # 🔽 NUEVOS CAMPOS (Mercado Pago)
    mp_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mp_status = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    mercadopago_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"

    def __str__(self):
        return f"Orden #{self.id}"

    def get_total(self):
        return sum(item.get_total_price() for item in self.items.all())



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name}"

    def get_total_price(self):
        return self.price * self.quantity
