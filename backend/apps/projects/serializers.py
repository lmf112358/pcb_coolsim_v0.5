"""projects 序列化器（F2-001~026 层级 CRUD）"""
from rest_framework import serializers
from .models import Project, Building, Floor, Room, ExtraLoad


class ProjectSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.city_name", read_only=True)

    class Meta:
        model = Project
        fields = ["id", "project_name", "project_code", "city", "city_name",
                  "location", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["id", "project", "building_name", "building_code",
                  "description", "sort_order", "created_at", "updated_at"]
        read_only_fields = ["id", "project", "created_at", "updated_at"]


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ["id", "building", "floor_name", "floor_area", "floor_height",
                  "floor_plan_file", "floor_plan_data", "sort_order", "created_at", "updated_at"]
        read_only_fields = ["id", "building", "created_at", "updated_at"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id", "floor", "room_name", "room_code", "area", "height", "volume",
            "temp_precision", "indoor_calc_temp", "indoor_calc_humidity",
            "civil_load_index", "lighting_load_index",
            "status", "sort_order", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "floor", "volume", "created_at", "updated_at"]


class RoomCopySerializer(serializers.Serializer):
    """F2-021: 复制功能区域"""
    room_name = serializers.CharField(max_length=100)
    floor = serializers.PrimaryKeyRelatedField(queryset=Floor.objects.all(), required=False)
