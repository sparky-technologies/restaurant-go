from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response

from utils.utils import send_otp
from .serializers import UserSerializer
from django.core.cache import cache
from utils.exceptions import handle_internal_server_exception
from utils.response import service_response


class CreateUserAPIView(APIView):
    """
    Create a new user. and sends an otp to the user email address
    """

    serializer_class = UserSerializer

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
                    status_code=200,
                )
            else:
                return service_response(
                    status="error", message=serializer.errors, status_code=404
                )

        except Exception:
            return handle_internal_server_exception()


class RootPage(APIView):
    def get(self, request, format=None):
        return service_response(
            status="success", message="Great, Welcome all good!", status_code=200
        )
