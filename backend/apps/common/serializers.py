"""common 序列化器"""
from rest_framework import serializers
from .models import CityConfig, WaterTempConfig


class CityConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityConfig
        fields = "__all__"


class WaterTempConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterTempConfig
        fields = ["id", "project", "temp_type_name", "supply_temp", "return_temp",
                  "description", "created_at", "updated_at"]
        read_only_fields = ["id", "project", "created_at", "updated_at"]
