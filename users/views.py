import hmac
import json
from typing import Union
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.utils import send_otp, send_reset_otp
from .serializers import (
    AddressSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    UpdatePasswordSerializer,
)
from django.core.cache import cache
from utils.exceptions import handle_internal_server_exception
from utils.response import service_response
from drf_yasg.utils import swagger_auto_schema
from .models import DeliveryAddress, Tray, User, Funding
from drf_yasg import openapi
from .swagger_serializer import ResponseSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import logging
import traceback
import os
import requests
from requests.auth import HTTPBasicAuth
import uuid
import hashlib
import urllib.parse
from dotenv import load_dotenv
from rest_framework import viewsets
from utils.serializers import serialize_model
from rest_framework.exceptions import MethodNotAllowed
from utils.exceptions import ValidationException

load_dotenv()


logger = logging.getLogger(__name__)


machine = os.getenv("MACHINE")

base_url = os.getenv("MONNIFY_BASE_URL_RG")
api_key = os.getenv("MONNIFY_API_KEY_RG")
secret_key = os.getenv("MONNIFY_SECRET_KEY_RG")
contract_code = os.getenv("MONNIFY_CONTRACT_CODE_RG")
auth_url = f"{base_url}/api/v1/auth/login"


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
                user = serializer.save()
                # send the otp to the email
                otp: Union[str, None] = send_otp(email, username)
                if otp is None:
                    return service_response(
                        status="error",
                        message=_("Unable to send OTP"),
                        status_code=404,
                    )
                # cache the otp
                cache.set(email, otp, 60 * 10)  # otp expires in 10 mins
                # create a Tray object for the user
                Tray.objects.create(user=user)
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
        except ValidationException as e:
            return service_response(status="error", message=e.message, status_code=409)

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
                    "expires_in": 86400000000,  # in microseconds
                }

                now: datetime = datetime.now()
                user.last_login = now
                user.save()
                # TODO Implement RabbitMQ queue to another email service to send new login email to user
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
        try:
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
                key = email
                reset_key = f"Reset_Token:{otp}"
                user.reset_token = otp
                user.save()
                cache.set(key, otp, 60 * 10)
                cache.set(reset_key, otp, 60 * 10)
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
        except Exception:
            return handle_internal_server_exception()


class ChangePasswordView(APIView):
    """
    Updates a user password
    """

    serializer_class = ChangePasswordSerializer

    def post(self, request):
        """
        POST request handler for updating user password
        """
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                token = serializer.validated_data.get("reset_token")
                password = serializer.validated_data.get("password1")
                try:
                    user = User.objects.get(reset_token=token)
                    key = f"Reset_Token:{token}"
                    if cache.get(key):
                        user.set_password(password)
                        user.reset_token = None
                        user.save()
                        return service_response(
                            status="success",
                            message="Password successfully updated",
                            status_code=status.HTTP_200_OK,
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
        except ValidationException as e:
            return service_response(
                status="error",
                message=e.message,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return handle_internal_server_exception()


class UpdatePasswordView(APIView):
    """View for updating an authenticated user password"""

    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """POST request handler"""
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                password = serializer.validated_data.get("password")
                user = User.objects.get(email=request.user.email)
                user.set_password(password)
                user.save()
                return service_response(
                    status="sucess",
                    message="Password sucessfully updated",
                    status_code=status.HTTP_200_OK,
                )
            return service_response(
                status="error",
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return handle_internal_server_exception()


class MonnifyCardChargeAPIView(APIView):
    """Charge User with their card details through monnify"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """Charge user with card details"""

        def is_americanexpress(card_number: str) -> bool:
            """checks if card is american express type

            Args:
                card_number (str): card number

            Returns:
                bool: True or false
            """
            if card_number.startswith("37") or card_number.startswith("34"):
                return True
            return False

        def is_luhns_valid(card_number: str) -> bool:
            """Luhns Algorithm to validate card number

            Args:
                card_number (str): card number

            Returns:
                bool: True or false
            """
            try:
                if not (16 <= len(card_number) <= 19):
                    return False
                # convert to digitis
                digits = list(map(int, card_number[::-1]))
                total_sum = 0
                for i, digit in enumerate(digits):
                    if i % 2 == 1:
                        digit *= 2
                        if digit > 9:
                            digit -= 9
                    total_sum += digit
                return total_sum % 10 == 0

            except Exception as e:
                logger.error(f"{e}")
                traceback.print_exc()
                return False

        try:
            card_number = request.data.get("card_number")
            expiry_month = request.data.get("expiry_month")
            expiry_year = request.data.get("expiry_year")
            pin = request.data.get("pin")
            cvv = request.data.get("cvv")
            user = request.user
            amount = request.data.get("amount")
            card_date = datetime(int(expiry_year), int(expiry_month), 1)
            today = datetime.now()
            # bypass validation for dev mode
            if machine != "local":
                if card_date < today:
                    return service_response(
                        status="error", message="Card has Expired", status_code=400
                    )
                is_express = is_americanexpress(card_number)
                is_luhn_valid = is_luhns_valid(card_number)
                if is_express:
                    if len(cvv) != 4:
                        return service_response(
                            status="error", message="Invalid CVV", status_code=400
                        )
                else:
                    if len(cvv) != 3:
                        return service_response(
                            status="error", message="Invalid CVV", status_code=400
                        )
                if not is_luhn_valid:
                    return service_response(
                        status="error", message="Invalid Card Number", status_code=400
                    )
                # monnify card charge
            if amount:
                response = requests.post(
                    auth_url, auth=HTTPBasicAuth(f"{api_key}", f"{secret_key}")
                )
                token = response.json()["responseBody"]["accessToken"]

                referrence_id = str(uuid.uuid4())[:8]
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(token),
                }
                body = {
                    "amount": float(amount),
                    "customerName": f"{user.username}",
                    "customerEmail": f"{user.email}",
                    "paymentReference": f"{referrence_id}",
                    "paymentDescription": f"Restaurant Go Wallet Funding by {user.username} at {datetime.now()}",
                    "currencyCode": "NGN",
                    "contractCode": f"{contract_code}",
                    # "redirectUrl": f"{redirect_url}",
                    "paymentMethods": ["CARD"],
                }
                data = json.dumps(body)
                url = f"{base_url}/api/v1/merchant/transactions/init-transaction"
                response = requests.post(url, headers=headers, data=data)
                res = response.json()
                print(res)
                tran_ref = res["responseBody"]["transactionReference"]
                init_tran_url = f"{base_url}/api/v1/merchant/cards/charge"
                charge_body = {
                    "transactionReference": tran_ref,
                    "collectionChannel": "API_NOTIFICATION",
                    "card": {
                        "number": card_number,
                        "expiryMonth": expiry_month,
                        "expiryYear": expiry_year,
                        "pin": pin,
                        "cvv": cvv,
                    },
                }
                charge_data = json.dumps(charge_body)
                payment_response = requests.post(
                    init_tran_url, data=charge_data, headers=headers
                )
                res = payment_response.json()
                print(res)
                req_success = res.get("requestSuccessful")
                res_message = res.get("responseMessage")
                if req_success and res_message == "success":
                    res_body = res.get("responseBody")
                    if res_body["status"] == "SUCCESS":
                        response = {
                            "status": "success",
                            "message": "Card Charge Successful",
                            "data": res_body,
                        }
                        return service_response(
                            status="success",
                            message="Card Charge Successful",
                            data=res_body,
                            status_code=200,
                        )
                return service_response(
                    status="error", message="Card Charge Failed", status_code=400
                )

        except Exception:
            return handle_internal_server_exception()


class MonnifyTransferAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            print(user)
            data = request.data
            amount = data.get("amount")
            if amount:
                response = requests.post(
                    auth_url, auth=HTTPBasicAuth(f"{api_key}", f"{secret_key}")
                )
                print(api_key, secret_key)
                print(response.json())
                token = response.json()["responseBody"]["accessToken"]
                referrence_id = str(uuid.uuid4())[:8]
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(token),
                }
                body = {
                    "amount": float(amount),
                    "customerName": f"{user.username}",
                    "customerEmail": f"{user.email}",
                    "paymentReference": f"{referrence_id}",
                    "paymentDescription": f"Restaurant Go Wallet Funding by {user.username} at {datetime.now()}",
                    "currencyCode": "NGN",
                    "contractCode": f"{contract_code}",
                    # "redirectUrl": f"{redirect_url}",
                    "paymentMethods": ["ACCOUNT_TRANSFER"],
                }
                data = json.dumps(body)
                url = f"{base_url}/api/v1/merchant/transactions/init-transaction"
                response = requests.post(url, headers=headers, data=data)
                res = response.json()
                print(res)
                # checkout_url = res["responseBody"]["checkoutUrl"]
                tran_ref = res["responseBody"]["transactionReference"]
                init_tran_url = f"{base_url}/api/v1/merchant/bank-transfer/init-payment"
                print(init_tran_url)
                body = {"transactionReference": f"{tran_ref}", "bankCode": "035"}
                init_data = json.dumps(body)
                payment_response = requests.post(
                    init_tran_url, data=init_data, headers=headers
                )
                res = payment_response.json()
                print(res)
                res_body = res.get("responseBody")
                expiry_time = res_body["expiresOn"]
                amount = res_body["amount"]
                # 0.5% charge fee
                fee = round(float(amount) * 0.005)
                acct_details = {
                    "account_number": res_body["accountNumber"],
                    "account_name": res_body["accountName"],
                    "bank_name": res_body["bankName"],
                    "bank_code": res_body["bankCode"],
                    "charges_fee": fee,
                    "expiry_time": expiry_time,
                    "ussd": res_body["ussdPayment"],
                    "tran_ref": res_body["transactionReference"],
                    "amount": amount,
                }
                return service_response(
                    status="success",
                    message="Account details generated successfully",
                    data=acct_details,
                    status_code=200,
                )
            else:
                return service_response(
                    status="error", message="Amount is required", status_code=400
                )
        except Exception:
            return handle_internal_server_exception()


class MonnifyPaymentWebhook(APIView):
    """Monnify webhook controller for payment notifications"""

    def post(self, request, *args, **kwargs):
        """Post endpoint for the monnify webhook"""
        try:
            # get thr payload
            data = request.body
            dat = json.loads(data)
            monnify_hashkey = request.META["HTTP_MONNIFY_SIGNATURE"]
            forwarded_for = "{}".format(request.META.get("REMOTE_ADDR"))
            monnify_secret = os.getenv("MONNIFY_SECRET_KEY_RG")
            monnify_api_key = os.getenv("MONNIFY_API_KEY_RG")
            monnify_base_url = os.getenv("MONNIFY_BASE_URL_RG")
            if machine == "local":
                ip = "127.0.0.1"
            else:
                ip = "35.242.133.146"
            secret = bytes(monnify_secret, "utf-8")
            hashkey = hmac.new(secret, request.body, hashlib.sha512).hexdigest()
            if hashkey == monnify_hashkey and forwarded_for == ip:
                res = requests.post(
                    f"{monnify_base_url}/api/v1/auth/login",
                    auth=HTTPBasicAuth(f"{monnify_api_key}", f"{monnify_secret}"),
                )
                data = json.loads(res.text)

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(
                        data["responseBody"]["accessToken"]
                    ),
                }
                response = requests.get(
                    "{}/api/v2/transactions/{}".format(
                        monnify_base_url,
                        urllib.parse.quote(dat["eventData"]["transactionReference"]),
                    ),
                    headers=headers,
                )

                resp = json.loads(response.text)

                if (
                    response.status_code == 200 and resp["requestSuccessful"] == True
                ) and (
                    resp["responseMessage"] == "success"
                    and resp["responseBody"]["paymentStatus"] == "PAID"
                ):
                    user_email = dat["eventData"]["customer"]["email"]
                    user = User.objects.get(email__iexact=user_email)
                    amount = float(resp["responseBody"]["amountPaid"])
                    our_fee = round(float(amount) * 0.005)

                    paynow = float(amount) - float(our_fee)

                    ref = resp["responseBody"]["transactionReference"]

                    if not Funding.objects.filter(ref=ref).exists():
                        try:
                            user.deposit(
                                user.id,
                                paynow,
                                "Wallet Funding",
                                ref,
                            )
                            Funding.objects.create(
                                user=user,
                                ref=ref,
                                amount=paynow,
                                status="Successful",
                                gateway="monnify",
                            )
                            return HttpResponse(status=200)
                        except Exception as e:
                            logger.error(f"{e}")
                            traceback.print_exc()
                            return HttpResponse(status=500)

                    else:
                        pass

                else:
                    return HttpResponse(status=400)

            else:
                return HttpResponseForbidden("Permission denied.")

        except Exception as e:
            logger.error(f"{e}")
            traceback.print_exc()
            return HttpResponse(status=500)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer

    def update(self, request, pk=None):
        """Updates a user"""
        try:
            data = request.data
            user = User.objects.get(pk=pk)
            user_id = user.id
            fields_to_update = [
                "first_name",
                "last_name",
                "phone_number",
                "profile_pic",
            ]
            for field, value in data.items():
                if field not in fields_to_update:
                    return service_response(
                        status="error",
                        message=f"You are not allowed to change {field} field",
                        status_code=404,
                    )
                setattr(user, field, value)

            # Save the user
            user.save()
            # cache the updata user
            keys_to_remove = ["password", "groups", "user_permissions"]
            user_full_name = user.full_name
            data = serialize_model(user, keys_to_remove)
            data["user_id"] = user_id
            data["full_name"] = user_full_name
            cache.set(f"user:{user_id}", data, 60 * 60 * 12)  # expires in 12 hours
            return service_response(
                status="success", message="User updated successfully", status_code=200
            )
        except User.DoesNotExist:
            return service_response(
                status="error", message="User Not Found!", status_code=404
            )
        except Exception:
            return handle_internal_server_exception()

    def retrieve(self, request, pk=None):
        """Retrieves a user

        Args:
            request (dict): HTTP Request object
            pk (int, optional): model primary key. Defaults to None.
        """
        try:
            request_user = request.user
            # get user from cache
            print(f"This is {pk}")
            user = cache.get(f"user:{pk}")
            if user:
                print("Fetch from cache")
                if request_user.id != user.get("user_id"):
                    return service_response(
                        status="error",
                        message="You are not allowed to access this user",
                        status_code=403,
                    )
                return service_response(
                    status="success",
                    message="User retrieved successfully",
                    data=user,
                    status_code=200,
                )
            else:
                user = User.objects.get(pk=pk)
                user_id = user.id
                print("Fetch From db")
                if request_user.id != user.id:
                    return service_response(
                        status="error",
                        message="You are not allowed to access this user",
                        status_code=403,
                    )
                user_full_name = user.full_name
                keys_to_remove = ["password", "groups", "user_permissions"]
                data = serialize_model(user, keys_to_remove)
                print(pk)
                data["user_id"] = user_id
                data["full_name"] = user_full_name
                cache.set(f"user:{user_id}", data, 60 * 60 * 12)  # expires in 12 hours
                return service_response(
                    status="success",
                    message="User retrieved successfully",
                    data=data,
                    status_code=200,
                )
        except User.DoesNotExist:
            return service_response(
                status="error", message="User Not Found!", status_code=404
            )
        except Exception:
            return handle_internal_server_exception()

    def destroy(self, request, pk=None):
        raise MethodNotAllowed(request.method)

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        secure_actions = ["update", "retrieve"]
        if self.action in secure_actions:
            return [IsAuthenticated()]
        else:
            return []


class GetUserInfoAPIView(APIView):
    """UserInfo API View Handler

    Args:
        APIView (_type_): _description_
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            # get the user from db
            user = User.objects.get(pk=user.id)
            user_id = user.id
            user_full_name = user.full_name
            keys_to_remove = [
                "password",
                "groups",
                "user_permissions",
                "reset_token",
                "is_staff",
                "is_superuser",
            ]
            data = serialize_model(user, keys_to_remove)
            data["user_id"] = user_id
            data["full_name"] = user_full_name
            return service_response(
                status="success",
                data=data,
                message="Successfully Fetched",
                status_code=200,
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
                        "data": {"wallet_balance": 0},
                    }
                },
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="User not authenticated",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "User not authenticated",
                        "data": {},
                    }
                },
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Internal server error",
                schema=ResponseSerializer(),
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Internal server error",
                        "data": {},
                    }
                },
            ),
        },
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


class AddressViewSet(viewsets.ModelViewSet):
    """Address management viewset"""

    queryset = DeliveryAddress.objects.all()
    serializer_class = AddressSerializer
    permission_class = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create new user address"""
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                # get the DeliveryAddress and count to check if greater than 3
                count = DeliveryAddress.objects.filter(user=request.user).count()
                if count == 3:
                    return service_response(
                        status="error",
                        message="User already has 3 addresses",
                        data=None,
                        status_code=400,
                    )
                serializer.save()
                return service_response(
                    status="success",
                    message="Address created successfully",
                    data=serializer.data,
                    status_code=201,
                )
            error_message = serializer.errors["message"][0]
            return service_response(
                status="error",
                message=error_message,
                data=None,
                status_code=400,
            )
        except Exception:
            return handle_internal_server_exception()

    def partial_update(self, request, *args, **kwargs):
        """Partially updates user address"""
        try:
            # get address instance
            address = self.get_object()
            serializer = self.serializer_class(
                address, context={"request": request}, data=request.data, partial=True
            )
            if serializer.is_valid():
                self.perform_update(serializer)
                return service_response(
                    status="success",
                    data=serializer.data,
                    message="Address Update Successfully",
                    status_code=200,
                )

            return service_response(
                status="error", message=serializer.errors["message"][0], status_code=400
            )
        except Exception:
            return handle_internal_server_exception()

    def destroy(self, request, *args, **kwargs):
        """Delete user address"""
        try:
            address = self.get_object()
            address.delete()
            return service_response(
                status="success",
                message="Address deleted successfully",
                data=None,
                status_code=204,
            )
        except Exception:
            return handle_internal_server_exception()

    def list(self, request, *args, **kwargs):
        """List all user addresses"""
        try:
            addresses = DeliveryAddress.objects.filter(user=request.user)
            serializer = self.serializer_class(
                addresses, many=True, context={"request": request}
            )
            data = serializer.data
            return service_response(
                status="success",
                message="Addresses retrieved successfully",
                data=data,
                status_code=200,
            )
        except Exception:
            return handle_internal_server_exception()
