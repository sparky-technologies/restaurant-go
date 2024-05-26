from rest_framework.serializers import Serializer
from rest_framework import serializers


class ResponseSerializer(Serializer):

    status = serializers.CharField()
    message = serializers.CharField()
    # status_code = serializers.IntegerField()
    data = serializers.DictField(required=False)
