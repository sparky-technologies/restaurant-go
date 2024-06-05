from rest_framework import serializers

from foods.models import FoodAsset, FoodItem, FoodPackage


class FoodAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAsset
        fields = ("name", "image", "alt")


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ("name", "quantity", "price", "description")


class FoodPackageSerializer(serializers.ModelSerializer):
    items = FoodItemSerializer(many=True)
    assets = FoodAssetSerializer(many=True)

    class Meta:
        model = FoodPackage
        fields = (
            "id",
            "name",
            "price",
            "discount_price",
            "available_quantity",
            "items",
            "assets",
        )
