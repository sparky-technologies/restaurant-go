#!/usr/bin/env python3

"""Contains User related serializers"""

from users.models import MainUser
from rest_framework import serializers


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for signing up a user
    """
    class Meta:
        model = MainUser
        fields = ('email', 'username', 'password', 'first_name', 'last_name')
