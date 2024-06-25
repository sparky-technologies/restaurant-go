from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from utils.decorators import str_meta


# Create your models here.


@str_meta
class FoodCategory(models.Model):
    name = models.CharField(max_length=100)


class FoodPackage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        null=True, blank=True, help_text=_("Package Description")
    )
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        related_name="category",
        blank=True,
        null=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    available_quantity = models.IntegerField(default=0)
    total_purchase = models.BigIntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} {self.price}"

    class Meta:
        verbose_name = "Food Package"
        verbose_name_plural = "Food Packages"

    def reduce_quantity(self) -> None:
        """This is a util method to reduce the quantity"""
        if self.available_quantity > 0:
            self.available_quantity -= 1
            self.save()

    def increase_total_purchase(self) -> None:
        """This is a util method to increase the the total purchase"""
        self.total_purchase += 1
        self.save()


class FoodAsset(models.Model):
    name = models.CharField(max_length=100)
    food_package = models.ForeignKey(
        FoodPackage, on_delete=models.CASCADE, related_name="assets"
    )
    image = models.ImageField(
        upload_to="food_images",
        null=True,
        blank=True,
    )
    alt = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Food Asset"
        verbose_name_plural = "Food Assets"


class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        null=True, blank=True, help_text=_("Simple description of the item")
    )
    food_package = models.ForeignKey(
        FoodPackage, on_delete=models.CASCADE, related_name="items"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"


@str_meta
class Food(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        null=True, blank=True, help_text=_("Package Description")
    )
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        related_name="food_category",
        blank=True,
        null=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    available_quantity = models.IntegerField(default=0)
    total_purchase = models.BigIntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def reduce_quantity(self):
        """This is a util method to reduce the quantity"""
        if self.available_quantity > 0:
            self.available_quantity -= 1
            self.save()

    def increase_total_purchase(self) -> None:
        """This is a util method to increase the the total purchase"""
        self.total_purchase += 1
        self.save()
