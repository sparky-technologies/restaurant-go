from rest_framework import routers
from django.urls import path, include

from foods.views import FoodCategoryAPIView, FoodPackageViewSet

router = routers.DefaultRouter()

router.register(r"foods", FoodPackageViewSet, basename="foods")

urlpatterns = [
    path("", include(router.urls)),
    path("foods/categories", FoodCategoryAPIView.as_view(), name="foods-categories")
]
