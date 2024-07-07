import pytest
from rest_framework.test import APIClient, APIRequestFactory
from django.contrib.auth import get_user_model

from foods.models import Food
from .models import Order, OrderItem
from .serializers import TrayItemSerializer
from .views import (
    AddItemToTrayAPIView,
    UpdateTrayItemQuantityAPIView,
    TrayItemListAPIView,
)

User = get_user_model()


# Fixtures for shared setup
@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def create_user():
    user = User.objects.create_user(
        username="testuser", password="12345", email="ayo@test.com"
    )
    return user


@pytest.fixture
def create_order(create_user):
    order = Order.objects.create(
        user=create_user,
        status="pending",
        order_id="566636",
        total_amount=2599,
        delivery_address="Some address",
    )
    return order


@pytest.fixture
def create_food():
    food = Food.objects.create(name="some food", price=24)
    return food


@pytest.fixture
def create_order_item(create_order):
    order_item = OrderItem.objects.create(
        order=create_order, quantity=2, food_item_id=1, food_item_type="Meal"
    )
    return order_item


@pytest.fixture
def api_request_factory():
    return APIRequestFactory()


# Tests
@pytest.mark.django_db
def test_order_creation(create_order):
    assert create_order.user.username == "testuser"
    assert create_order.status == "pending"


@pytest.mark.django_db
def test_order_item_creation(create_order_item, create_order):
    assert create_order_item.order == create_order
    assert create_order_item.quantity == 2
