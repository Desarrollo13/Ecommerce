from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product_name", "price", "quantity")
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("first_name", "email")
    inlines = [OrderItemInline]
