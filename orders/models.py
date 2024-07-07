from django.db import models
from django.contrib.auth import get_user_model
from constants.constant import order_status, payment_status, payment_type, food_types
from django.utils import timezone
from utils.decorators import str_meta

from foods.models import FoodItem, FoodPackage


User = get_user_model()

# Create your models here.


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100, choices=order_status, default="Pending")
    order_id = models.CharField(max_length=100)
    payment_status = models.CharField(
        max_length=30, choices=payment_status, default="UnPaid"
    )
    payment_type = models.CharField(
        max_length=30, choices=payment_type, default="OnDelivery"
    )
    delivery_address = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - Order {self.id}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        db_table = "orders"


@str_meta
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food_item_id = models.IntegerField()
    food_item_type = models.CharField(max_length=50, choices=food_types, default="Meal")
    quantity = models.IntegerField(default=1)

    def subtotal(self) -> float:
        if self.food_item_type == "Meal":
            return float(self.quantity) * float(
                FoodItem.objects.get(id=self.food_item_id).price
            )
        elif self.food_item_type == "Package":
            return float(self.quantity) * float(
                FoodPackage.objects.get(id=self.food_item_id).price
            )
        return 0

    def increase_quantity(self):
        self.quantity += 1
        self.save()

        return self.quantity
