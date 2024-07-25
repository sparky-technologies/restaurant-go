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
    groups_link = serializers.SerializerMethodField()
    self_link = serializers.SerializerMethodField()

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
            "groups_link",
            "self_link",
        )

    def get_groups_link(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri("/")[:-1]
        url = f"{base_url}/foods"
        return url

    def get_self_link(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri("/")[:-1]
        url = f"{base_url}/foods/{obj.id}"
        return url


class FoodSerializer(serializers.ModelSerializer):
    assets = AssetFoodSerializer(many=True)
    groups_link = serializers.SerializerMethodField()
    self_link = serializers.SerializerMethodField()

    class Meta:
        model = Food
        fields = "__all__"

    def get_groups_link(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri("/")[:-1]
        url = f"{base_url}/foods"
        return url

    def get_self_link(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri("/")[:-1]
        url = f"{base_url}/foods/{obj.id}"
        return url
