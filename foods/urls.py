from rest_framework import routers
from django.urls import path, include

from foods.views import FoodPackageViewSet

router = routers.DefaultRouter()

router.register(r"foods", FoodPackageViewSet, basename="foods")

urlpatterns = [
    path("", include(router.urls)),
]
