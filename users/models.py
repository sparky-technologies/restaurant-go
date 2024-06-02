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
