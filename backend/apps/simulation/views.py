"""动态仿真 API（F6-020~023）"""
import numpy as np
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import Room
from apps.calculation.models import RoomCalcResult
from .models import SimulationRun
from .services import simulate_weather_driven, aggregate_extremes


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_simulation(request):
    """POST /api/v1/simulations/ 触发动态仿真（F6-020~022）

    body: {room_id, weather: {temp_dry[], temp_wet[], pressure[]}}
    """
    room_id = request.data.get("room_id")
    weather = request.data.get("weather", {})

    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        return Response({"detail": "功能区域不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 检查静态计算桥梁
    if not RoomCalcResult.objects.filter(room=room).exists():
        return Response(
            {"detail": "请先完成静态计算（Q_terminal 桥梁缺失）"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 构造 numpy 气象序列
    try:
        n = len(weather["temp_dry"])
        timestamps = np.array([
            np.datetime64("2024-01-01") + np.timedelta64(i, "h") for i in range(n)
        ])
        w = {
            "timestamps": timestamps,
            "temp_dry": np.array(weather["temp_dry"], dtype=float),
            "temp_wet": np.array(weather["temp_wet"], dtype=float),
            "pressure": np.array(weather["pressure"], dtype=float),
        }
        result = simulate_weather_driven(room, w)
        extremes = aggregate_extremes(result["total_load"], timestamps)
    except Exception as e:
        return Response({"detail": f"仿真失败：{e}"}, status=status.HTTP_400_BAD_REQUEST)

    sim_run = SimulationRun.objects.create(
        room=room, mode="weather_driven", status="SUCCESS",
        result_summary={
            "extremes": extremes,
            "point_count": n,
            "max_load": float(result["total_load"].max()),
        },
    )

    return Response({
        "batch_id": str(sim_run.batch_id),
        "room_id": room.id,
        "mode": sim_run.mode,
        "status": sim_run.status,
        "point_count": n,
        "extremes": extremes,
        "total_load": result["total_load"].tolist(),
    }, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_simulation(request, batch_id: str):
    """GET /api/v1/simulations/{batch_id}/ 获取仿真结果（F7-032）"""
    sim = get_object_or_404(SimulationRun, batch_id=batch_id)
    return Response({
        "batch_id": str(sim.batch_id),
        "room_id": sim.room_id,
        "mode": sim.mode,
        "status": sim.status,
        "result_summary": sim.result_summary,
        "created_at": sim.created_at,
    })
