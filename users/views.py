from datetime import datetime
from typing import Union

from django.core.cache import cache
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from utils.exceptions import handle_internal_server_exception
from utils.response import service_response
from utils.utils import send_otp
from .models import User
from .serializers import LoginSerializer, UserSerializer
from .swagger_serializer import ResponseSerializer


class CreateUserAPIView(APIView):
    """
    Create a new user. and sends an otp to the user email address
    """

    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Create a new user",
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                schema=ResponseSerializer(),
                description="User created successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Registration Successful, An OTP has been sent to your email",
                        "data": {}
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                schema=ResponseSerializer(),
                description="Bad request",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "User with username|email already exists.",
                        "data": {}
                    }
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                schema=ResponseSerializer(),
                description="Unable to send OTP",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Unable to send OTP",
                        "data": {}
                    }
                }
            )
            ,
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                schema=ResponseSerializer(),
                description="Internal server error",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Internal server error",
                        "data": {}
                    }}
            ),
        },
    )
    def post(self, request) -> Response:
        """Post handler to create a new user"""
        try:
            serializer: UserSerializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                # get the user username and email
                email: Union[str, None] = serializer.validated_data.get("email")
                username: Union[str, None] = serializer.validated_data.get("username")
                # save the user
                serializer.save()
                # send the otp to the email
                otp: Union[str, None] = send_otp(email, username)
                if otp is None:
                    return service_response(
                        status="error", message=_("Unable to send OTP"), status_code=404
                    )
                # cache the otp
                cache.set(email, otp, 60 * 10)  # otp expires in 10 mins
                return service_response(
                    status="success",
                    message=_(
                        f"Registration Successful, An OTP has been sent to your email {email}"
                    ),
                    status_code=201,
                )
            else:
                return service_response(
                    status="error", message=serializer.errors, status_code=400
                )

        except Exception:
            return handle_internal_server_exception()


class RootPage(APIView):

    @swagger_auto_schema(
        operation_description="Root page",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Root page api response",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Great, Welcome all good!",
                        "data": {}
                    }

                }
            )
        }
    )
    def get(self, request, format=None):
        return service_response(
            status="success", message="Great, Welcome all good!", status_code=200
        )


class VerifyOTP(APIView):
    """
    Verify the otp sent to the user email address
    """

    @swagger_auto_schema(
        operation_description="Verify the otp",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Information needed for verification",
            required=["email", "otp"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, default="example@mail.com"),
                "otp": openapi.Schema(type=openapi.TYPE_STRING, default="123456")
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful verification",
                schema=ResponseSerializer,
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "OTP verified",
                        "data": {}
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Expired or invalid otp send with request.",
                schema=ResponseSerializer,
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Invalid OTP",
                        "data": {}
                    }
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                schema=ResponseSerializer(),
                description="Internal server error",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Internal server error",
                        "data": {}
                    }}
            ),
        }
    )
    def post(self, request, *args, **kwargs) -> Response:
        """Post handler to verify the otp sent to the user"""
        try:
            email: Union[str, None] = request.data.get("email")
            otp: Union[str, None] = request.data.get("otp")
            # retrieve otp from cache with the email
            cache_otp: Union[str, None] = cache.get(email)
            print(cache_otp)
            if otp is None:
                return service_response(
                    status="error", message=_("Invalid OTP"), status_code=400
                )
            # check if the otp sent by the user matches the otp in the cache
            if str(otp) == str(cache_otp):
                user: User = User.objects.get(email=email)
                user.email_verified = True
                user.save()
                # delete the otp from the cache if correct
                cache.delete(email)
                return service_response(
                    status="success", message=_("OTP verified"), status_code=200
                )
            else:
                return service_response(
                    status="error", message=_("Invalid OTP"), status_code=400
                )

        except Exception:
            return handle_internal_server_exception()


class ResendOTP(APIView):
    """
    Resend the otp to the user email address
    """

    @swagger_auto_schema(
        operation_description="Resend the otp",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The email address",
                    example="example@mail.com",
                )
            },
            required=['email']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Resend the otp",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "An OTP has been sent to your email {{user_email}}",
                        "data": {}
                    }}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad request",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "User does not exist",
                        "data": {}
                    }
                }
            ),

            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Unable to send OTP",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Unable to send OTP",
                        "data": {}
                    }
                }),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Internal server error",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Internal server error",
                        "data": {}
                    }})
        }
    )
    def post(self, request, *args, **kwargs) -> Response:
        """resend the otp"""
        try:
            email: Union[str, None] = request.data.get("email")
            # find the user by email
            user: User = User.objects.get(email__iexact=email)
            username = user.username
            # send the otp to the email
            otp = send_otp(email, username)
            if otp is None:
                return service_response(
                    status="error", message=_("Unable to send OTP"), status_code=404
                )
            # cache the otp
            cache.set(email, otp, 60 * 10)  # otp expires in 10 mins
            return service_response(
                status="success",
                message=_(f"An OTP has been sent to your email {email}"),
                status_code=200,
            )
        except User.DoesNotExist:
            return service_response(
                status="error", message=_("User does not exist"), status_code=400
            )
        except Exception:
            return handle_internal_server_exception()


class UserLoginAPIView(APIView):
    """Generates user access tokens"""

    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="Login a user",
        request_body=LoginSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(

                description="Login successful",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Login Successful",
                        "data": {
                            "access_token": "eyJ______________________",
                            "refresh_token": "eyJ______________________",
                            "expires_in": 3600
                        },
                        "data": {}
                    }}),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad request",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": {
                            "email": ["This field is required."],
                            "password": ["This field is required."]
                        },
                        "data": {}
                    }
                }),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Internal server error",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Internal server error",
                        "data": {}
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs) -> Response:
        """Generates user access tokens"""
        try:
            serializer: LoginSerializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                # get the user from the serializer validated data
                user = serializer.validated_data.get("user")
                # get the token
                tokens = RefreshToken.for_user(user)
                access_token = str(tokens.access_token)
                refresh_token = str(tokens)
                # Construct token data response
                token_data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": tokens.access_token.lifetime.total_seconds(),  # Expiry time in seconds
                }
                now: datetime = datetime.now()
                user.last_login = now
                user.save()
                return service_response(
                    status="success",
                    message="Login Successful",
                    data=token_data,
                    status_code=200,
                )
            else:
                return service_response(
                    status="error", message=serializer.errors, status_code=400
                )
        except Exception:
            return handle_internal_server_exception()


class SocialAuth(APIView):
    """Create user with just email and username from social auth response and login"""

    def post(self, request, *args, **kwargs) -> Response:
        """Post handler to create user with username and email"""
        try:
            data = request.data
            # get or create user from db
            user, created = User.objects.get_or_create(**data)
            print(created)
            # get the tokens
            tokens = RefreshToken.for_user(user)
            access_token = str(tokens.access_token)
            refresh_token = str(tokens)
            # Construct token data response
            token_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": tokens.access_token.lifetime.total_seconds(),
            }
            now: datetime = datetime.now()
            user.last_login = now
            user.email_verified = True
            user.save()
            return service_response(
                status="success",
                message="Login Successful",
                data=token_data,
                status_code=200,
            )
        except IntegrityError:
            return service_response(
                status="error",
                message="User with the email or username already exist",
                status_code=400,
            )
        except Exception:
            return handle_internal_server_exception()


class WalletView(APIView):
    """View to get the user wallet balance"""

    @swagger_auto_schema(
        operation_description="Get the user wallet balance",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Wallet balance retrieved",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Wallet balance retrieved",
                        "data": {
                            "wallet_balance": 0
                        }
                    }
                }
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authenticated",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "User not authenticated",
                        "data": {}
                    }
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Internal server error",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Internal server error",
                        "data": {}
                    }
                }
            )
        }
    )
    def get(self, request, *args, **kwargs) -> Response:
        """Get the user wallet balance"""

        try:
            if not request.user.is_authenticated:
                return service_response(
                    status="error",
                    message="User not authenticated",
                    status_code=401,
                )
            user = request.user
            wallet_balance = user.wallet_balance
            return service_response(
                status="success",
                message="Wallet balance retrieved",
                data={"wallet_balance": wallet_balance},
                status_code=200,
            )
        except Exception:
            return handle_internal_server_exception()

# TODO: implement get userinfo view can use viewsets to immplement retrieve and update in one viewset
# TODO: implement password reset endpoints
# TODO: implement change password endpoint should required authentication
