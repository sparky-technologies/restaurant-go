from django.urls import path
from .views import *

urlpatterns = [
    path("register", CreateUserAPIView.as_view(), name="register"),
    path("otp/verify", VerifyOTP.as_view(), name="verify-otp"),
]
