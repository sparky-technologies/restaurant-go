from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("register", CreateUserAPIView.as_view(), name="register"),
    path("otp/verify", VerifyOTP.as_view(), name="verify-otp"),
    path("otp/resend", ResendOTP.as_view(), name="resend-otp"),
    path("login", UserLoginAPIView.as_view(), name="login"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
