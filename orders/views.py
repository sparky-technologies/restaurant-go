from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from foods.models import Food, FoodPackage
from orders.serializers import TrayItemSerializer
from users.models import Tray, TrayItem, DeliveryAddress
from utils.response import service_response
from utils.exceptions import handle_internal_server_exception
from django.views.decorators.cache import never_cache
from utils.utils import generate_ref
from .models import Order, OrderItem
from utils.mails import sendmail

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
            print(tray.items.all())
            serializer = self.serializer_class(
                tray.items.all(), context={"request": request}, many=True
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


class CheckoutAPIView(APIView):
    """Checkout the Tray"""

    permission_classes = [IsAuthenticated]
    """
    Requires
    User address selected id
    tray items
    charge user if instant payment and set payment and set payment status Paid and Set payment_type to Instant

    """

    def post(self, request, *args, **kwargs):
        """Checkout post handler"""
        try:
            user = request.user
            data = request.data
            # add data validation for address and payment_type
            address_id = data.get("address_id")
            address_instance = DeliveryAddress.objects.get(id=int(address_id))
            city = address_instance.city
            address = address_instance.address
            payment_type = data.get("payment_type")
            if (
                payment_type.capitalize() != "Instant"
                and payment_type.capitalize() != "OnDelivery"
            ):
                return service_response(
                    status="error",
                    data=None,
                    message="Invalid payment type",
                    status_code=400,
                )
            tray = Tray.objects.get(user=user)
            if tray.items.count() == 0:
                return service_response(
                    status="error",
                    data=None,
                    message="Tray is empty, please add items to the tray",
                    status_code=400,
                )
            total_amount = 0
            order_id = generate_ref()
            full_address = f"{city} - {address}"
            for item in tray.items.all():
                if item.food_item_type == "Meal":
                    food = Food.objects.get(id=item.food_item_id)
                    if item.quantity > food.available_quantity:
                        return service_response(
                            status="error",
                            data=None,
                            message=f"Not enough stock for {food.name} in this quantity",
                            status_code=402,
                        )
                    food.available_quantity -= item.quantity
                    food.save()
                elif item.food_item_type == "Pacakge":
                    package = FoodPackage.objects.get(id=item.food_item_id)
                    if item.quantity > package.available_quantity:
                        return service_response(
                            status="error",
                            data=None,
                            message=f"Not enough stock for {package.name} in this quantity",
                            status_code=402,
                        )
                    package.available_quantity -= item.quantity
                    package.save()
                # TODO: Add delivery amount charge
                total_amount += item.subtotal()

            if payment_type.capitalize() == "Instant":
                # charge the user instantly
                message = user.debit(user.id, total_amount, "Food Purchase", order_id)
                if message == "Low Funds":
                    return service_response(
                        status="error",
                        data=None,
                        message="Insufficient Funds, Please fund your wallet or select pay on delivery cash or transfer!",
                        status_code=402,
                    )
                elif message == "Error":
                    return handle_internal_server_exception()
                elif message == "Debited":
                    # create order
                    order = Order.objects.create(
                        user=user,
                        total_amount=total_amount,
                        delivery_address=full_address,
                        order_id=order_id,
                    )
                    order.payment_status = "Paid"
                    order.payment_type = "Instant"
                    order.save()
            else:
                order = Order.objects.create(
                    user=user,
                    total_amount=total_amount,
                    delivery_address=full_address,
                    order_id=order_id,
                )

            for item in tray.items.all():
                # reduce stock
                if item.food_item_type == "Meal":
                    food = Food.objects.get(id=item.food_item_id)
                    food.increase_total_purchase(item.quantity)
                elif item.food_item_type == "Package":
                    package = FoodPackage.objects.get(id=item.food_item_id)
                    package.increase_total_purchase(item.quantity)
                # create the order items
                OrderItem.objects.create(
                    order=order,
                    food_item_type=item.food_item_type,
                    food_item_id=item.food_item_id,
                    quantity=item.quantity,
                )
            tray.items.all().delete()
            data = {
                "order_id": order.order_id,
            }
            # TODO: add send admin and user a notification mail
            user_email = user.email
            username = user.username
            admin_message = f"New Order with id {order.order_id} has been placed, visit the admin page to view order and process accordingly."
            user_message = "Thank your for your order, your order as been received and now processing, One of our delivery agent will contact you soon for the delivery of your order. Thank you for choosing us!"
            subject = "Restaurant Go Order Notification"
            sendmail(
                subject=subject,
                message=user_message,
                user_email=user_email,
                username=username,
            )
            admin_subject = "New Order Alert"
            sendmail(
                subject=admin_subject,
                message=admin_message,
                user_email="truebone005@gmail.com",
                username="Admin",
            )

            return service_response(
                status="success",
                data=data,
                message="Order Successfully Placed",
                status_code=200,
            )
        except DeliveryAddress.DoesNotExist:
            return service_response(
                status="error",
                data=None,
                message="Invalid Address",
                status_code=404,
            )
        except Exception:
            return handle_internal_server_exception()
