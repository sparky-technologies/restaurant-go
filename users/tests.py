import pytest
from unittest import mock
from rest_framework.test import APIRequestFactory
from .views import CreateUserAPIView
from .serializers import UserSerializer
from utils.utils import send_otp
from utils.exceptions import handle_internal_server_exception
from django.core.cache import cache
from .models import User
from utils.response import service_response


@pytest.fixture
def request_factory():
    return APIRequestFactory()


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "truebone002@gmail.com",
        "password1": "Testpassword0@",
        "password2": "Testpassword0@",
    }


@pytest.fixture
def bad_data():
    return {
        "username": "testuser",
        "email": "truebone002@gmail.com",
        "password1": "Testpassword@",
        "password2": "Testpassword@",
    }


@pytest.mark.django_db
def test_post_valid_data(request_factory, user_data, mocker):
    view = CreateUserAPIView.as_view()
    request = request_factory.post("/api/v1/register/", user_data)
    serializer = UserSerializer(data=user_data)
    serializer.is_valid()
    mocker.patch("utils.utils.send_otp", return_value="123456")
    response = view(request)
    assert response.status_code == 201
    assert "Registration Successful" in response.data.get("message")
