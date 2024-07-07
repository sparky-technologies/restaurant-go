from rest_framework import serializers

from foods.models import Food, FoodPackage
from foods.serializers import FoodPackageSerializer, FoodSerializer
from users.models import TrayItem


# class UpdateTrayItemQuantitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TrayItem
#         fields = ("quantity", "price", "discount_price")


class TrayItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrayItem
        fields = (
            "id",
            "food_item_id",
            "food_item_type",
            "quantity",
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        food_type = instance.food_item_type
        food_item_id = instance.food_item_id

        if food_type == "Meal":
            food_item_obj = Food.objects.get(id=food_item_id)
            food = FoodSerializer(food_item_obj).data
        elif food_type == "Package":
            food_item_obj = FoodPackage.objects.get(id=food_item_id)
            food = FoodPackageSerializer(food_item_obj).data
        else:
            food = None

        ret["food"] = food

        ret.pop("food_item_type", None)
        ret.pop("food_item_id", None)

        return ret
