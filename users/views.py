#!/usr/bin/env python3

"""Contains user related views"""

from django.contrib.auth import authenticate
from django.contrib.auth import login
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import (
    MainUser,
    SignUpSerializer
)
from utils.email_utils import EmailUtils

Mail = EmailUtils()


class SignUpViewSet(viewsets.ModelViewSet):
    """Signup View"""

    serializer_class = SignUpSerializer
    queryset = MainUser.objects.all()

    def create(self, request, *args, **kwargs):
        """Create a new user"""

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            verification_code = Mail.generate_verification_code()
            user = MainUser.custom_save(**serializer.validated_data,
                                        verification_code=verification_code)
            Mail.send_verification_email(user, verification_code)
            return Response({
                "message":
                    "You have successfully signed up. Please check your"
                    " email for the verification code",
                "status":
                    status.HTTP_201_CREATED,
            })
        return Response({
            "error": serializer.errors,
            "status": status.HTTP_400_BAD_REQUEST
        })
