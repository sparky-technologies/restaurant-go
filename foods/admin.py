from django.contrib import admin

from foods.models import FoodAsset, FoodItem, FoodPackage, FoodCategory, Food

# Register your models here.


class FoodAssetAdmin(admin.StackedInline):
    model = FoodAsset
    extra = 1


class FoodItemStackedAdmin(admin.StackedInline):
    model = FoodItem
    extra = 1


class FoodPackageAdmin(admin.ModelAdmin):
    inlines = [FoodAssetAdmin, FoodItemStackedAdmin]
    list_display = ["name", "category", "price", "available_quantity", "total_purchase"]
    list_filter = ["category"]
    search_fields = [
        "name",
    ]


class FoodAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "available_quantity", "total_purchase"]
    list_filter = ["category"]
    search_fields = [
        "name",
    ]


admin.site.register(FoodPackage, FoodPackageAdmin)
admin.site.register(FoodCategory)
admin.site.register(Food, FoodAdmin)
