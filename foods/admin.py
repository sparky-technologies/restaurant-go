from django.contrib import admin

from foods.models import FoodAsset, FoodItem, FoodPackage

# Register your models here.


class FoodAssetAdmin(admin.StackedInline):
    model = FoodAsset
    extra = 1


class FoodItemStackedAdmin(admin.StackedInline):
    model = FoodItem
    extra = 1


class FoodPackageAdmin(admin.ModelAdmin):
    inlines = [FoodAssetAdmin, FoodItemStackedAdmin]


admin.site.register(FoodPackage, FoodPackageAdmin)
