"""projects 视图（F2-001~026 层级 CRUD + F2-021 复制）"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Building, Floor, Room
from .serializers import (
    ProjectSerializer, BuildingSerializer, FloorSerializer,
    RoomSerializer, RoomCopySerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """项目 CRUD（F1-015~023）"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class BuildingViewSet(viewsets.ModelViewSet):
    """建筑 CRUD（F2-009~011）"""
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer

    def create(self, request, project_pk=None, *args, **kwargs):
        """POST /projects/{projectId}/buildings/"""
        project = get_object_or_404(Project, pk=project_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = Building.objects.all()
        project_id = self.kwargs.get("project_pk") or self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class FloorViewSet(viewsets.ModelViewSet):
    """楼层 CRUD（F2-012~013）"""
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer

    def create(self, request, building_pk=None, *args, **kwargs):
        building = get_object_or_404(Building, pk=building_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(building=building)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = Floor.objects.all()
        building_id = self.kwargs.get("building_pk") or self.request.query_params.get("building")
        if building_id:
            qs = qs.filter(building_id=building_id)
        return qs


class RoomViewSet(viewsets.ModelViewSet):
    """功能区域 CRUD（F2-014~020）+ F2-021 复制"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def create(self, request, floor_pk=None, *args, **kwargs):
        floor = get_object_or_404(Floor, pk=floor_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(floor=floor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="copy")
    def copy(self, request, pk=None):
        """F2-021: 复制功能区域

        POST /rooms/{id}/copy/  body: {"room_name": "新名称"}
        """
        source = get_object_or_404(Room, pk=pk)
        serializer = RoomCopySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 复制参数到新房间
        new_room = Room.objects.create(
            floor=serializer.validated_data.get("floor", source.floor),
            room_name=serializer.validated_data["room_name"],
            room_code=source.room_code,
            area=source.area, height=source.height,
            civil_load_index=source.civil_load_index,
            lighting_load_index=source.lighting_load_index,
            personnel_load_index=source.personnel_load_index,
            personnel_count=source.personnel_count,
            electric_equipment_power=source.electric_equipment_power,
            electric_equipment_coefficient=source.electric_equipment_coefficient,
            heated_equipment_power_with_exhaust=source.heated_equipment_power_with_exhaust,
            heated_equipment_coefficient_with_exhaust=source.heated_equipment_coefficient_with_exhaust,
            heated_equipment_power_without_exhaust=source.heated_equipment_power_without_exhaust,
            heated_equipment_coefficient_without_exhaust=source.heated_equipment_coefficient_without_exhaust,
            heat_exhaust_volume=source.heat_exhaust_volume,
            acid_exhaust_volume=source.acid_exhaust_volume,
            alkali_exhaust_volume=source.alkali_exhaust_volume,
            organic_exhaust_volume=source.organic_exhaust_volume,
            dust_exhaust_volume=source.dust_exhaust_volume,
            pressure_diff=source.pressure_diff,
            indoor_calc_temp=source.indoor_calc_temp,
            indoor_calc_humidity=source.indoor_calc_humidity,
            temp_precision=source.temp_precision,
            cleanliness_level=source.cleanliness_level,
        )
        return Response(RoomSerializer(new_room).data, status=status.HTTP_201_CREATED)
