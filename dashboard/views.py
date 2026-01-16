from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from orders.models import Order, OrderItem


@staff_member_required
def dashboard_home(request):
    total_orders = Order.objects.count()
    paid_orders = Order.objects.filter(status="paid").count()
    pending_orders = Order.objects.filter(status="pending").count()

    total_revenue = (
        OrderItem.objects.aggregate(
            total=Sum("price")
        )["total"] or 0
    )

    recent_orders = Order.objects.all()[:5]

    context = {
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
    }

    return render(request, "dashboard/index.html", context)
