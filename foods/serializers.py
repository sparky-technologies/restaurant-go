from rest_framework import serializers

from foods.models import AssetFood, Food, FoodAsset, FoodItem, FoodPackage


class FoodAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAsset
        fields = ("name", "image", "alt")


class AssetFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetFood
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
            "total_purchase",
        )


class FoodSerializer(serializers.ModelSerializer):
    assets = AssetFoodSerializer(many=True)

    class Meta:
        model = Food
        fields = "__all__"
