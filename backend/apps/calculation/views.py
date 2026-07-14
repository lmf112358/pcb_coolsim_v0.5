"""静态冷量计算 API（F4-001）"""
from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.calculation.services import calc_static
from apps.projects.models import Room
from .models import RoomCalcResult


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def calc_static_view(request, room_id: int):
    """触发单房间静态冷量计算，结果落库 RoomCalcResult

    POST /api/v1/calc/static/{roomId}/
    """
    try:
        room = Room.objects.select_related(
            "floor__building__project__city"
        ).get(pk=room_id)
    except Room.DoesNotExist:
        return Response({"detail": "功能区域不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 执行计算（PRD §15 6 步流水线）
    result = calc_static(room)

    # 落库 RoomCalcResult（OneToOne，update_or_create 保证幂等）
    RoomCalcResult.objects.update_or_create(
        room=room,
        defaults={
            "civil_load": result["civil"],
            "lighting_load": result["lighting"],
            "personnel_load": result["personnel"],
            "electric_equipment_load": result["electric"],
            "heated_equipment_load": result["heated"],
            "terminal_load": result["terminal"],
            "total_exhaust_volume": result["total_exhaust"],
            "infiltration_air_volume": result["infiltration"],
            "fresh_air_volume": result["fresh_air"],
            "indoor_enthalpy_calc": result["h_indoor"],
            "outdoor_enthalpy_calc": result["h_outdoor"],
            "enthalpy_diff": result["enthalpy_diff"],
            "cold_load_index": result["cold_load_index"],
        },
    )

    return Response(
        {
            "room_id": room.id,
            "room_name": room.room_name,
            "terminal_load": str(result["terminal"]),
            "fresh_air_load": str(result["fresh_air_load"]),
            "total_load": str(result["total_load"]),
            "cold_load_index": str(result["cold_load_index"]) if result["cold_load_index"] else None,
        },
        status=status.HTTP_201_CREATED,
    )
