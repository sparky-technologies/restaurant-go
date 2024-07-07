from django.contrib import admin

from orders.models import Order, OrderItem

# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "total_amount",
        "payment_status",
        "payment_type",
        "created_at",
    )
    search_fields = ["order_id", "user__username"]
    list_filter = ["created_at", "payment_status", "payment_type"]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
