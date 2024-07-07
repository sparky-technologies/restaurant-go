from typing import List
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Prefetch
from foods.models import AssetFood, Food, FoodAsset, FoodCategory, FoodItem, FoodPackage
from foods.serializers import FoodPackageSerializer, FoodSerializer
from utils.exceptions import handle_internal_server_exception
from utils.response import service_response
from rest_framework.exceptions import MethodNotAllowed
from django.db.models import Prefetch
from rest_framework.views import APIView

# Create your views here.


# noinspection PyUnresolvedReferences
class FoodPackageViewSet(viewsets.ModelViewSet):
    """Food Package REST Viewset"""

    queryset = FoodPackage.objects.all()
    serializer_class = FoodPackageSerializer

    def list(self, request, *args, **kwargs) -> Response:
        """List all food packages"""
        try:
            # get food category
            category = request.query_params.get("category", None)
            items_fields: List[str] = ["name", "quantity", "price", "description"]
            assets_fields: List[str] = ["name", "image", "alt"]
            if category:
                cat_id = int(category)
                foods: List[FoodPackage] = FoodPackage.objects.prefetch_related(
                    Prefetch("items", queryset=FoodItem.objects.only(*items_fields)),
                    Prefetch("assets", queryset=FoodAsset.objects.only(*assets_fields)),
                ).filter(category=cat_id)
            else:
                foods: List[FoodPackage] = FoodPackage.objects.prefetch_related(
                    Prefetch("items", queryset=FoodItem.objects.only(*items_fields)),
                    Prefetch("assets", queryset=FoodAsset.objects.only(*assets_fields)),
                ).all()
            serializer: FoodPackageSerializer = FoodPackageSerializer(foods, many=True)
            data = serializer.data
            return service_response(
                status="success", data=data, message="Fetch Successful", status_code=200
            )
        except Exception:
            return handle_internal_server_exception()

    def retrieve(self, request, *args, **kwargs) -> Response:
        """Retrieve a food package"""
        try:
            items_fields: List[str] = ["name", "quantity", "price", "description"]
            assets_fields: List[str] = ["name", "image", "alt"]
            food: FoodPackage = FoodPackage.objects.prefetch_related(
                Prefetch("items", queryset=FoodItem.objects.only(*items_fields)),
                Prefetch("assets", queryset=FoodAsset.objects.only(*assets_fields)),
            ).get(id=kwargs["pk"])
            serializer: FoodPackageSerializer = FoodPackageSerializer(food)
            data = serializer.data
            return service_response(
                status="success", data=data, message="Fetch Successful", status_code=200
            )
        except Exception:
            return handle_internal_server_exception()

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)


class FoodCategoryAPIView(APIView):
    """API endpoint to list all available food categories"""

    def get(self, request, *args, **kwargs) -> Response:
        """http get handler that returns all available food categories"""
        try:
            food_categories: List[FoodCategory] = FoodCategory.objects.all().values()
            data: List[dict] = list(food_categories)
            return service_response(
                status="success", data=data, message="Fetch Successful", status_code=200
            )
        except:
            return handle_internal_server_exception()


class FoodViewSet(viewsets.ModelViewSet):
    """Food API View set"""

    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def list(self, request, *args, **kwargs) -> Response:
        """List all available foods"""
        try:
            category = request.query_params.get("category", None)
            assets_fields: List[str] = ["name", "image", "alt"]
            if category:
                cat_id = int(category)
                foods: List[Food] = Food.objects.prefetch_related(
                    Prefetch("assets", queryset=AssetFood.objects.only(*assets_fields)),
                ).filter(category=cat_id)
            else:
                foods: List[Food] = Food.objects.prefetch_related(
                    Prefetch("assets", queryset=AssetFood.objects.only(*assets_fields)),
                ).all()
            serializer: FoodSerializer = FoodSerializer(foods, many=True)
            data = serializer.data
            return service_response(
                status="success", data=data, message="Fetch Successful", status_code=200
            )
        except Exception:
            return handle_internal_server_exception()
