from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# Create your models here.


class FoodPackage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        null=True, blank=True, help_text=_("Package Description")
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name + " " + self.price

    class Meta:
        verbose_name = "Food Package"
        verbose_name_plural = "Food Packages"


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
