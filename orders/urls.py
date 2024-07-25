from django.urls import path, include

from orders.views import (
    AddItemToTrayAPIView,
    CheckoutAPIView,
    TrayItemListAPIView,
    UpdateTrayItemQuantityAPIView,
)


urlpatterns = [
    path("tray/add", AddItemToTrayAPIView.as_view(), name="add-to-tray"),
    path(
        "tray/<int:item_id>/quantity/update/",
        UpdateTrayItemQuantityAPIView.as_view(),
        name="update-item-quantity",
    ),
    path(
        "tray/items",
        TrayItemListAPIView.as_view(),
        name="tray-items",
    ),
    path("tray/checkout", CheckoutAPIView.as_view(), name="checkout"),
]
