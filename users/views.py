from typing import Union
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.utils import send_otp, send_reset_otp
from .serializers import LoginSerializer, UserSerializer, ChangePasswordSerializer, UpdatePasswordSerializer
from django.core.cache import cache
from utils.exceptions import handle_internal_server_exception
from utils.response import service_response
from drf_yasg.utils import swagger_auto_schema
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class CreateUserAPIView(APIView):
    """
    Create a new user. and sends an otp to the user email address
    """

    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Create a new user",
        responses={
            201: "Registration successful, An OTP has been sent to your email",
            400: "Bad request",
            500: "Internal server error",
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
    def get(self, request, format=None):
        return service_response(
            status="success", message="Great, Welcome all good!", status_code=200
        )


class VerifyOTP(APIView):
    """
    Verify the otp sent to the user email address
    """

    def post(self, request, *args, **kwargs) -> Response:
        """Post handler to verify the otp sent to the user"""
        try:
            email: Union[str, None] = request.data.get("email")
            otp: Union[str, None] = request.data.get("otp")
            # retrieve otp from cache with the email
            cache_otp: Union[str, None] = cache.get(email)
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


class PasswordResetView(APIView):
    """Sends reset token to a user"""

    def post(self, request):
        """
        Post handler for sending reset OTP
        """
        email: Union[str, None] = request.data.get("email")
        if not email:
            return service_response(
                status="error",
                message="Please provide an email address",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return service_response(
                status="error",
                message="Please provide a valid email address",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        otp: Union[str, None] = send_reset_otp(email)
        if otp:
            key = f'Reset_Token:{otp}'
            user.reset_token = otp
            user.save()
            cache.set(key, otp, 60 * 10)
            return service_response(
                status="success",
                message=(f"Reset OTP has been sent to your email {email}"),
                status_code=status.HTTP_200_OK,
            )
        else:
            return service_response(
                status="error",
                message="Failed to send reset OTP",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordView(APIView):
    """
    Updates a user password
    """
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        """
        POST request handler for updating user password
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data.get("reset_token")
            password = serializer.validated_data.get("password")
            try:
                user = User.objects.get(reset_token=token)
                key = f'Reset_Token:{token}'
                if cache.get(key):
                    user.set_password(password)
                    user.reset_token = None
                    user.save()
                    return service_response(
                        status="sucess",
                        message="Password sucessfully updated",
                        status_code=status.HTTP_200_OK
                    )
                return service_response(
                    status="error",
                    message="Invalid or expired RESET OTP",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            except User.DoesNotExist:
                return service_response(
                    status="error",
                    message="Invalid or expired RESET OTP",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        return service_response(
            status="error",
            message=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UpdatePasswordView(APIView):
    """View for updating an authenticated user password"""
    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """POST request handler"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.get("password")
            user = User.objects.get(email=request.user.email)
            user.set_password(password)
            user.save()
            return service_response(
                status="sucess",
                message="Password sucessfully updated",
                status_code=status.HTTP_200_OK
            )
        return service_response(
            status="error",
            message=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
# TODO: implement get userinfo view can use viewsets to immplement retrieve and update in one viewset
