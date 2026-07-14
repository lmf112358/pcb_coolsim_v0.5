"""forecast 序列化器"""
from rest_framework import serializers
from .models import ForecastScenario, ForecastHourlyResult


class ForecastScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastScenario
        fields = ["id", "project", "name", "start_date", "weather_source",
                  "status", "created_at", "updated_at"]
        read_only_fields = ["id", "project", "created_at", "updated_at"]
