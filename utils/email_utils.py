#!/usr/bin/env python3

"""
Handles all utils relating to sending emails and also generating tokens
"""
from django.conf import settings
from os import getenv
from utils.redis_utils import RedisClient
from users.models import MainUser as User
import secrets
import requests
from dotenv import load_dotenv
from django.template.loader import render_to_string

load_dotenv()
API_KEY = getenv("ELASTIC_EMAIL_KEY")
SENDER = getenv("EMAIL_SENDER")
redis_cli = RedisClient()


class EmailUtils:
    @staticmethod
    def generate_verification_code(length=6):
        """
        Generate a random verification code.
        :param length: Length of the verification code (default is 6)
        :return: Random verification code
        """
        charset = "0123456789"
        verification_code = ''.join(secrets.choice(charset) for _ in range(length))
        return verification_code

    @staticmethod
    def send_verification_email(user: "User", verification_code: int):
        url = "https://api.elasticemail.com/v2/email/send"
        context = {
            'verification_code': verification_code,
            'username': user.username,

        }
        html_template = render_to_string("users/verify.html", context)
        key = f'user_id:{user.id}:{verification_code}'
        request_payload = {
            "apikey": API_KEY,
            "from": getenv("EMAIL_SENDER"),
            "to": user.email,
            "subject": "Verify your account",
            "bodyHtml": html_template,
            "isTransactional": False,
        }

        try:
            response = requests.post(url, data=request_payload)
            if response.status_code == 200:
                if response.json()['success']:
                    redis_cli.set_key(key, verification_code, expiry=10)
                    return True
            else:
                print(f'Error sending verification email to {user.email}')
                return False
        except Exception as e:
            print(f'Error sending verification email to {user.email}: {str(e)}')
            return False
