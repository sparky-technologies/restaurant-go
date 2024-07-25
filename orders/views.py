from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from foods.models import Food, FoodPackage
from orders.serializers import TrayItemSerializer
from users.models import Tray, TrayItem
from utils.response import service_response
from utils.exceptions import handle_internal_server_exception
from django.views.decorators.cache import never_cache

# Create your views here.


class AddItemToTrayAPIView(APIView):
    """Add an item to the Tray"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Add to tray post handler"""
        try:
            # get user from the request
            user = request.user

            data = request.data

            # get the food from the request payload
            food_type = data.get("type")
            print(food_type)
            if food_type != "Meal" and food_type != "Package":
                return service_response(
                    status="error",
                    data=None,
                    message="Invalid food type",
                    status_code=400,
                )

            food_item_id = int(data.get("item_id"))

            if food_type == "Meal":
                # get the food item
                food_item = Food.objects.get(id=food_item_id)
            elif food_type == "Package":
                # get the food package
                food_item = FoodPackage.objects.get(id=food_item_id)

            quantity = data.get("quantity", 1)
            # get the user tray
            tray, created = Tray.objects.get_or_create(user=user)
            # create a new tray item
            TrayItem.objects.create(
                tray=tray,
                food_item_type=food_type,
                quantity=quantity,
                food_item_id=int(food_item_id),
            )
            tray_count = Tray.objects.get(user=user).items.count()
            data = {
                "items_count": tray_count,
            }
            return service_response(
                status="success",
                data=data,
                message="Item Successfully Added To Tray",
                status_code=200,
            )
        except Food.DoesNotExist:
            return service_response(
                status="error",
                data=None,
                message="This Food Does Not Exist",
                status_code=404,
            )
        except FoodPackage.DoesNotExist:
            return service_response(
                status="error",
                data=None,
                message="This Food Package Does Not Exist",
                status_code=404,
            )
        except Exception:
            return handle_internal_server_exception()


class UpdateTrayItemQuantityAPIView(APIView):
    """Update the quantity of an item in the Tray"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Update quantity post handler"""
        try:
            item_id = kwargs.get("item_id")
            # get the TrayItem
            tray_item = TrayItem.objects.get(id=item_id)

            # update the quantity
            quantity = tray_item.increase_quantity()

            data = {
                "quantity": quantity,
            }
            return service_response(
                status="success",
                data=data,
                message="Quantity Updated Successfully",
                status_code=200,
            )

        except TrayItem.DoesNotExist:
            return service_response(
                status="error",
                data=None,
                message="This Tray Item Does Not Exist",
                status_code=404,
            )
        except Exception:
            return handle_internal_server_exception()


class TrayItemListAPIView(APIView):
    """List all items in the Tray"""

    permission_classes = [IsAuthenticated]
    serializer_class = TrayItemSerializer

    def get(self, request, *args, **kwargs):
        """list all items in the tray"""
        try:
            user = request.user
            # get tray
            tray = Tray.objects.get(user=user)
            # serialize the tray items
            print(tray.items)
            serializer = self.serializer_class(
                tray.items, context={"request": request}, many=True
            )
            return service_response(
                status="success",
                data=serializer.data,
                message="Tray Items Fetch Successfully",
                status_code=200,
            )
        except Tray.DoesNotExist:
            return service_response(
                status="error",
                data=None,
                message="This User Has No Tray",
                status_code=404,
            )
        except Exception:
            return handle_internal_server_exception()
