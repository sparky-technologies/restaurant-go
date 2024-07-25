from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
import logging
from django.core.validators import MinValueValidator
import traceback
from django.db import transaction
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
import random
import string
from constants.constant import food_types, state_choices, city_choices
from foods.models import Food, FoodItem, FoodPackage
from utils.decorators import str_meta

logger = logging.getLogger(__name__)


class CustomUserManager(UserManager):

    # email validator static method
    @staticmethod
    def validate_email(email: str) -> None:
        """
        This method validates the email address of a user.
        """
        try:
            validate_email(email)
        except ValidationError:
            logger.error(traceback.format_exc())
            raise ValidationError({"email": _("Please enter a valid email address.")})

    # create user method
    def create_user(
        self, email: str, username: str, password: str = "", **extra_fields: Any
    ) -> "User":
        """
        This method creates a user with the specified email address, username, and password.
        """
        if not email:
            logger.error(traceback.format_exc())
            raise ValueError("Users must have an email address.")
        if not username:
            logger.error(traceback.format_exc())
            raise ValueError("Users must have a username.")
        with transaction.atomic():
            user = self.model(email=email, username=username, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user


class User(AbstractUser, PermissionsMixin):
    """
    This class represents a user in the system.
    """

    objects = CustomUserManager()
    email = models.EmailField(verbose_name=_("Email address"), unique=True)
    username = models.CharField(
        verbose_name=_("Username"),
        max_length=30,
        unique=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
    )
    first_name = models.CharField(
        verbose_name=_("First name"), max_length=30, null=True, blank=True
    )
    last_name = models.CharField(
        verbose_name=_("Last name"), max_length=30, null=True, blank=True
    )
    wallet_balance = models.FloatField(
        default=0.00,
        null=True,
        validators=[MinValueValidator(0.0)],
    )
    phone_number = PhoneNumberField(blank=True, null=True)
    profile_pic = models.ImageField(
        verbose_name=_("Profile Image"),
        upload_to="media/profile_pic",
        height_field=None,
        width_field=None,
        max_length=200,
        blank=True,
        null=True,
    )
    email_verified = models.BooleanField(default=False)
    bvn = models.CharField(
        max_length=11, null=True, blank=True, help_text=_("User BVN Number")
    )
    reset_token = models.CharField(max_length=6, null=True, blank=True)

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return f"{self.username} - {self.email}"

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return f"{self.username}"

    @full_name.setter
    def full_name(self, first_name: str, last_name: str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.save()

    def _create_wallet_summary(
        self,
        amount: str,
        description: str,
        previous_balance: str,
        after_balance: str,
        status: str,
        order_id: str,
    ) -> None:
        """Create a new wallet summary instance.

        Args:
            amount (str): amount paid or debited
            description (str): wallet summary description
            previous_balance (str): previous wallet balance of the user
            after_balance (str): newly updated wallet balance of the user
            status (str): status of the wallet summary
            product_type (str): product type of the wallet summary
            tran_id (str): order id

        Returns:
            None: None
        """
        try:
            WalletSummary.objects.create(
                user=self,
                amount=amount,
                description=description,
                previous_balance=previous_balance,
                after_balance=after_balance,
                status=status,
                order_id=order_id,
            )
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())

    @classmethod
    def debit(cls, id, amount, description, order_id) -> str:
        """Debits a user

        Args:
            id (int): user's id
            amount (float): amount
            product_type (str): product type
            description (str): description
            order_id (str): order id

        Returns:
            str: message description
        """
        try:
            with transaction.atomic():
                user = cls.objects.select_for_update().get(id=id)
                previous_balance = user.wallet_balance
                if previous_balance < amount or amount < 0:
                    return "Low Funds"
                user.wallet_balance -= float(amount)
                user._create_wallet_summary(
                    amount=amount,
                    description=description,
                    previous_balance=previous_balance,
                    after_balance=(previous_balance - float(amount)),
                    status="Successful",
                    order_id=order_id,
                )
                user.save()
                return "Debited"
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            logger.error(traceback.format_exc())
            return "Error"

    @classmethod
    def deposit(cls, id, amount, description, order_id) -> bool:
        """Deposit fund for a user

        Args:
            id (user id): user's id
            amount (_type_): amount to be deposited
            product_type (_type_): product type of the deposit
            description (_type_): description of the deposit
            order_id (_type_): order id

        Returns:
            bool: True or False
        """
        try:
            with transaction.atomic():
                user = cls.objects.select_for_update().get(id=id)
                previous_balance = user.wallet_balance
                user.wallet_balance += float(amount)
                user._create_wallet_summary(
                    amount=amount,
                    description=description,
                    previous_balance=previous_balance,
                    after_balance=(previous_balance + float(amount)),
                    status="Successful",
                    order_id=order_id,
                )
                user.save()
                return True
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            logger.error(traceback.format_exc())
            return False


statuses = (
    ("Successful", "Successful"),
    ("Pending", "Pending"),
    ("Rejected", "Rejected"),
)


class Funding(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        blank=False,
        null=True,
        related_name="funding_history",
    )
    ref = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Payment Reference")
    )
    amount = models.FloatField(default=0.00, null=True, blank=True)
    status = models.CharField(
        max_length=50, null=True, blank=True, choices=statuses, default="Pending"
    )
    gateway = models.CharField(max_length=50, null=True, blank=True, default="Monnify")
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Fundings  Transactions"
        verbose_name = "Funding Transaction"

    def __str__(self):
        return f"Funding Transaction with {self.ref} for {self.user.username}"


status_choice = (
    ("Successful", "Successful"),
    ("Pending", "Pending"),
    ("Failed", "Failed"),
)


class WalletSummary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        blank=False,
        null=True,
        related_name="wallet_summary",
    )
    amount = models.CharField(
        max_length=50, blank=True, null=True, help_text="Amount Debited or Deposited"
    )
    description = models.CharField(
        max_length=200, blank=True, null=True, help_text="Description of the order"
    )
    previous_balance = models.CharField(
        max_length=200, blank=True, help_text="Previous Wallet Balance", null=True
    )
    after_balance = models.CharField(
        max_length=200, blank=True, help_text="Newly Updated Wallet Balance", null=True
    )
    status = models.CharField(
        max_length=100, blank=True, null=True, choices=status_choice
    )
    order_id = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.amount} Summary"

    class Meta:
        verbose_name_plural = "Wallet Summary"
        verbose_name = "Wallet Summary"


# Tray model another word for Cart in terms of Restaurant
@str_meta
class Tray(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tray",
        blank=False,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def generate_random_string(self) -> str:
        """utils function to generate a random string"""
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choices(characters, k=6))
        return random_string

    def save(self, *args, **kwargs):
        self.name = f"{self.user.username}RGO{self.generate_random_string()}"
        super().save(*args, **kwargs)


# TODO: enhance this model by removing the str_meta and customize nice __str__ and Meta for admin
@str_meta
class TrayItem(models.Model):
    tray = models.ForeignKey(Tray, on_delete=models.CASCADE, related_name="items")
    food_item_id = models.IntegerField()
    food_item_type = models.CharField(max_length=50, choices=food_types, default="Meal")
    quantity = models.IntegerField(default=1)

    def subtotal(self) -> float:
        if self.food_item_type == "Meal":
            return float(self.quantity) * float(
                Food.objects.get(id=self.food_item_id).price
            )
        elif self.food_item_type == "Package":
            return float(self.quantity) * float(
                FoodPackage.objects.get(id=self.food_item_id).price
            )
        return 0

    def increase_quantity(self):
        self.quantity += 1
        self.save()

        return self.quantity


class DeliveryAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="delivery_addresses"
    )
    state = models.CharField(max_length=30, default="Lagos")
    city = models.CharField(max_length=30, default="Island")
    address = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.state}, {self.city}"

    class Meta:
        verbose_name_plural = "Delivery Addresses"
        verbose_name = "Delivery Address"
        db_table = "delivery_addresses"
