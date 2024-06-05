from typing import List
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Prefetch
from foods.models import FoodAsset, FoodItem, FoodPackage
from foods.serializers import FoodPackageSerializer
from utils.exceptions import handle_internal_server_exception
from utils.response import service_response
from rest_framework.exceptions import MethodNotAllowed
from django.db.models import Prefetch

# Create your views here.


class FoodPackageViewSet(viewsets.ModelViewSet):
    """Food Package REST Viewset"""

    queryset = FoodPackage.objects.all()
    serializer_class = FoodPackageSerializer

    def list(self, request, *args, **kwargs) -> Response:
        """List all food packages"""
        try:
            items_fields: List[str] = ["name", "quantity", "price", "description"]
            assets_fields: List[str] = ["name", "image", "alt"]
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
                Prefetch(
                    "items", queryset=FoodItem.objects.only(*items_fields)
                ),
                Prefetch(
                    "assets", queryset=FoodAsset.objects.only(*assets_fields)
                ),
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
