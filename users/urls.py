from django.urls import path
from .views import (
    CreateUserAPIView,
    VerifyOTP,
    ResendOTP,
    UserLoginAPIView,
    SocialAuth,
    PasswordResetView,
    ChangePasswordView,
    UpdatePasswordView,
    status
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

decorated_refresh = swagger_auto_schema(
    method="post",
    operation_summary="Refresh JWT Token",
    operation_description="This endpoint allows users to refresh their JWT token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["refresh"],
        properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Token refreshed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access": openapi.Schema(type=openapi.TYPE_STRING),
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            examples={
                "application/json": {
                    "access": "eyJ0eXAi___",
                    "refresh": "eyJ0eXA___"
                }}
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="Token is invalid or expired",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"detail": "Token is invalid or expired"}}
        ),
    })(TokenRefreshView.as_view())

decorated_refresh = swagger_auto_schema(
    method="post",
    operation_summary="Refresh JWT Token",
    operation_description="This endpoint allows users to refresh their JWT token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["refresh"],
        properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Token refreshed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access": openapi.Schema(type=openapi.TYPE_STRING),
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            examples={
                "application/json": {
                    "access": "eyJ0eXAi___",
                    "refresh": "eyJ0eXA___"
                }}
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="Token is invalid or expired",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"detail": "Token is invalid or expired"}}
        ),
    })(TokenRefreshView.as_view())

urlpatterns = [
    path("register", CreateUserAPIView.as_view(), name="register"),
    path("otp/verify", VerifyOTP.as_view(), name="verify-otp"),
    path("otp/resend", ResendOTP.as_view(), name="resend-otp"),
    path("login", UserLoginAPIView.as_view(), name="login"),
    path("token/refresh", decorated_refresh, name="token_refresh"),
    path("social_auth", SocialAuth.as_view(), name="social_auth"),
    path("reset-password", PasswordResetView.as_view(), name="Reset-Password"),
    path("change-password", ChangePasswordView.as_view(), name='Change-Password'),
    path("update-password", UpdatePasswordView.as_view(), name="Update-Authenticated-user-password")
]
