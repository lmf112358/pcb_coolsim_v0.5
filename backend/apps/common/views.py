"""common 视图（F9 系统设置）"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import Project
from .models import CityConfig, WaterTempConfig
from .serializers import CityConfigSerializer, WaterTempConfigSerializer


class CityConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """国标参数查询（只读，F4-038~042/F9-011~013）"""
    queryset = CityConfig.objects.all()
    serializer_class = CityConfigSerializer

    def get_queryset(self):
        qs = CityConfig.objects.all()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(city_name__icontains=search) | Q(province__icontains=search))
        return qs


class WaterTempConfigViewSet(viewsets.ModelViewSet):
    """冷冻水温度配置 CRUD（F9-001~005）"""
    queryset = WaterTempConfig.objects.all()
    serializer_class = WaterTempConfigSerializer

    def create(self, request, project_pk=None, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = WaterTempConfig.objects.all()
        project_id = self.kwargs.get("project_pk") or self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_defaults(request):
    """默认值配置（F9-006~010）

    v0.5 返回系统默认值（四级继承后续实现）
    """
    return Response({
        "civil_load_index": 30, "lighting_load_index": 15,
        "personnel_load_index": 60,
        "indoor_calc_temp": 26, "indoor_calc_humidity": 55,
        "air_density": 1.2,
        "terminal_water_temp_default": "mid",
        "infiltration_coeff_table": [
            {"pressure_diff": 0, "k": 0.0}, {"pressure_diff": 1, "k": 1.0},
            {"pressure_diff": 2, "k": 1.5}, {"pressure_diff": 3, "k": 2.0},
            {"pressure_diff": 5, "k": 3.0}, {"pressure_diff": 10, "k": 3.5},
            {"pressure_diff": 15, "k": 4.0},
        ],
    })
