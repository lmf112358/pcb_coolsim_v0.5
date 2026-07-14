"""负荷预测 API 视图（F10-001~021）"""
from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.projects.models import Project, Room
from .models import ForecastScenario, ForecastHourlyResult
from .serializers import ForecastScenarioSerializer
from .services import seed_default_coefficients, forecast_room


class ForecastScenarioViewSet(viewsets.ModelViewSet):
    """预测场景 CRUD + 运行（F10-001~021）"""
    queryset = ForecastScenario.objects.all()
    serializer_class = ForecastScenarioSerializer

    def create(self, request, project_pk=None, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """F10-003/004: 状态切换"""
        sc = get_object_or_404(ForecastScenario, pk=pk)
        new_status = request.data.get("status")
        if new_status in ("active", "paused", "archived"):
            sc.status = new_status
            sc.save()
        return Response(ForecastScenarioSerializer(sc).data)

    @action(detail=True, methods=["post"], url_path="run")
    def run(self, request, pk=None):
        """F10-014~018: 运行预测"""
        sc = get_object_or_404(ForecastScenario, pk=pk)
        room_id = request.data.get("room_id")
        weather_temps = [Decimal(t) for t in request.data.get("weather_temps", [])]
        rates = [Decimal(r) for r in request.data.get("rates", [])]
        room = get_object_or_404(Room, pk=room_id)
        # 确保系数表已 seed
        seed_default_coefficients()
        results = forecast_room(room, weather_temps, rates)
        return Response({"results": [str(r) for r in results]})

    @action(detail=True, methods=["get"], url_path="results")
    def results(self, request, pk=None):
        """F10-018: 获取预测结果"""
        sc = get_object_or_404(ForecastScenario, pk=pk)
        results = sc.hourly_results.all().order_by("timestamp")
        data = [
            {
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "outdoor_temp": str(r.outdoor_temp),
                "predicted_load": str(r.predicted_load),
            }
            for r in results
        ]
        return Response({"results": data})

    def get_queryset(self):
        qs = ForecastScenario.objects.all()
        project_id = self.kwargs.get("project_pk") or self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs
