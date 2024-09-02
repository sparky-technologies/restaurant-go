"""
Django settings for restaurant_go project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import logging
import logging.config
from typing import Dict
from django.utils.log import DEFAULT_LOGGING
import os
from typing import Union
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ydal4wy$2pq6@r$x=gdgo%b!i7bh1l5ag$^uh2hbcipwxk4(n4"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

dev: Union[str, None] = os.getenv("dev")
print(f"Dev: {dev}")
ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # installed apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_yasg",
    "phonenumber_field",
    # django apps
    "users",
    "foods",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.cache.FetchFromCacheMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "restaurant_go.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_USER_MODEL = "users.User"

WSGI_APPLICATION = "restaurant_go.wsgi.application"


db_dict: Dict = {
    "areef": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DEV_NAME"),
        "USER": os.getenv("DEV_USER"),
        "PASSWORD": os.getenv("DEV_PASSWORD"),
        "HOST": os.getenv("DEV_HOST"),
        "PORT": os.getenv("DEV_PORT"),
    },
    "ayo": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "aliu": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "whyte": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 15,
}

CORS_ALLOW_ALL_ORIGINS = True

SWAGGER_SETTINGS = {
    "DEFAULT_AUTO_SCHEMA_CLASS": "drf_yasg.inspectors.SwaggerAutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1440),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": (
        db_dict.get(dev)
        if db_dict.get(dev)
        else {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    )
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "rifbackend001@gmail.com"
EMAIL_HOST_PASSWORD = "gtgt pbqu yljb evoz"


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lagos"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


logger = logging.getLogger(__name__)

LOG_LEVEL = "INFO"


try:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "file": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
            },
            "handlers": {
                "console": {
                    "level": LOG_LEVEL,
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                },
                "file": {
                    "level": LOG_LEVEL,
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file",
                    "filename": BASE_DIR / "logs" / "django.log",
                    "maxBytes": 1024 * 1024 * 10,  # 5 MB
                    "backupCount": 5,
                },
                "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
            },
            "loggers": {
                "": {
                    "level": LOG_LEVEL,
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
                "apps": {
                    "level": LOG_LEVEL,
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
            },
            "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        }
    )

except Exception:
    pass

REDIS_HOST = os.getenv("REDIS_URL", "localhost:6379")
redis_url = f"redis://{REDIS_HOST}"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": (
            redis_url
            if os.getenv("REDIS_URL")
            else "rediss://default:BeClknl6V7Jqr3rYmvZZLtvn7UAwMBfz@redis-15337.c62.us-east-1-4.ec2.redns.redis-cloud.com:15337"
        ),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 0,
    }
}

print(f'Cache: {CACHES["default"]["LOCATION"]}')
