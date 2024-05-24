from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.utils import send_otp
from .serializers import UserSerializer
from django.core.cache import cache
from utils.exceptions import handle_internal_server_exception
from utils.response import service_response
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model

User = get_user_model()


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
    def post(self, request):
        """Post handler to create a new user"""
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                # get the user username and email
                email = serializer.validated_data.get("email")
                username = serializer.validated_data.get("username")
                # save the user
                serializer.save()
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

    def post(self, request, *args, **kwargs):
        """Post handler to verify the otp sent to the user"""
        try:
            email = request.data.get("email")
            otp = request.data.get("otp")
            # retrieve otp from cache with the email
            cache_otp = cache.get(email)
            print(cache_otp)
            if otp is None:
                return service_response(
                    status="error", message=_("Invalid OTP"), status_code=400
                )
            # check if the otp sent by the user matches the otp in the cache
            if str(otp) == str(cache_otp):
                user = User.objects.get(email=email)
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
