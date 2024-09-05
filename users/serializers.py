import re
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from utils.exceptions import ValidationException

from users.models import DeliveryAddress


User = get_user_model()


class UserSerializer(ModelSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "phone_number",
            "email_verified",
        )

    def validate_password1(self, password1):
        """Validate user's inputed password on signup

        Args:
            password1 (str): user's password

        Raises:
            serializers.ValidationError: raise password requirements

        Returns:
            str: returns the validated password
        """
        # Regex pattern to match at least one digit, one uppercase letter,
        # one lowercase letter, one special character, and length >= 8
        regex_pattern = (
            r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )
        if not re.match(regex_pattern, password1):
            raise serializers.ValidationError(
                "Password must contain at least one digit, "
                "one uppercase letter, one lowercase letter, "
                "one special character, and length >= 8"
            )
        return password1

    def validate(self, data):
        """Validate user's inputed data on signup"""
        errors = {}
        email = data.get("email")
        username = data.get("username")
        password1 = data.get("password1")
        password2 = data.get("password2")
        if User.objects.filter(email__iexact=email):
            raise ValidationException(_("The email address is already in use"))
        if User.objects.filter(username__iexact=username):
            raise ValidationException(_("Username is taken!"))
        if password1 != password2:
            errors["password1"] = _("The two passwords do not match")
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        """Create a new user with the given validated data"""
        email = validated_data.get("email")
        password = validated_data.get("password1")
        username = validated_data.get("username")
        user = User.objects.create_user(
            email=email, username=username, password=password
        )
        return user


class LoginSerializer(ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(label="Username", required=False)
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        username = attrs.get("username")
        if email:
            user = User.objects.filter(email__iexact=email).first()
            if user and user.check_password(password):
                attrs["user"] = user
                return attrs
            else:
                raise serializers.ValidationError({"error": "Invalid credentials"})
        else:
            user = User.objects.filter(username__iexact=username).first()
            if user and user.check_password(password):
                attrs["user"] = user
                return attrs
            else:
                raise serializers.ValidationError({"error": "Invalid credentials"})

    class Meta:
        model = User
        fields = ("email", "username", "password")


class ChangePasswordSerializer(ModelSerializer):
    """Serializer for changing a user password"""

    password1 = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, data):
        """Validate user's inputed data on password change"""
        password1 = data.get("password1")
        password2 = data.get("password2")
        if password1 != password2:
            raise ValidationException(_("Password must match"))

    class Meta:
        model = User
        fields = ("password1", "reset_token", "password2")


class UpdatePasswordSerializer(ModelSerializer):
    """Serializer for updating a user password"""

    class Meta:
        model = User
        fields = ("password",)


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "profile_pic")


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    self_url = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryAddress
        fields = ("id", "state", "city", "address", "user", "self_url")

    def validate(self, data):
        """Validate user's inputed address on signup"""
        message = {"message": ""}
        state = data.get("state")
        city = data.get("city")
        if not state or not city:
            message["message"] = "State and city are required"
            raise serializers.ValidationError(message)
        if state.capitalize() != "Lagos":
            message["message"] = "We're running in Lagos only for now"
            raise serializers.ValidationError(message)
        if city.capitalize() != "Island":
            message["message"] = "We're running in Island only for now"
            raise serializers.ValidationError(message)
        return data

    def get_self_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri("/")[:-1]
        return f"{base_url}/users_addresses/{obj.pk}/"
