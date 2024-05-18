#!/usr/bin/env python3

"""Contains User model for the users app"""

from django.db import models
from typing import Any, Dict, Union
from django.utils import timezone
from uuid import uuid4
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group, Permission


class BaseModel(models.Model):
    """Base model for all models in the project
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class MainUser(AbstractUser, BaseModel):
    """
    The user model
    """

    email: str = models.EmailField(unique=True, max_length=50, null=False, blank=False)
    username: str = models.CharField(max_length=50, null=False, blank=False, unique=True)
    password: str = models.CharField(max_length=150, null=False, blank=False)
    first_name: str = models.CharField(max_length=50, null=False, blank=False)
    last_name: str = models.CharField(max_length=50, null=False, blank=False)
    is_verified: bool = models.BooleanField(default=False)
    reset_code: int = models.CharField(max_length=6, null=True, blank=True)
    verification_code: int = models.CharField(max_length=6, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name="mainuser_set",  # Custom related_name
        blank=True,
        help_text="The groups this user belongs to.",
        related_query_name="mainuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="mainuser_set",  # Custom related_name
        blank=True,
        help_text="Specific permissions for this user.",
        related_query_name="mainuser",
    )

    class Meta:
        indexes = [
            models.Index(fields=['email', 'username'])
        ]
        db_table = 'users'

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @classmethod
    def custom_save(cls, **kwargs: Dict[str, Union[str, Any]]) -> "MainUser":
        """Custom save method for the user model
        """
        if "password" in kwargs:
            kwargs["password"] = make_password(kwargs["password"])
        return cls.objects.create(**kwargs)
