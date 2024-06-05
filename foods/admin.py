from django.contrib import admin

from foods.models import FoodAsset, FoodItem, FoodPackage

# Register your models here.


class FoodAssetAdmin(admin.StackedInline):
    model = FoodAsset


class FoodItemStackedAdmin(admin.StackedInline):
    model = FoodItem


class FoodPackageAdmin(admin.ModelAdmin):
    inlines = [FoodAssetAdmin, FoodItemStackedAdmin]


admin.site.register(FoodPackage, FoodPackageAdmin)
