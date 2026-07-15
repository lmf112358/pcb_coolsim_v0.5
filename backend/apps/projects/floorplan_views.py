"""2D 平面图 API（F3-001~024）"""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Floor, Room
from .serializers import RoomSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_floor_plan_pdf(request, floor_id: int):
    """F3-001~003: 上传/替换底图 PDF"""
    floor = get_object_or_404(Floor, pk=floor_id)
    f = request.FILES.get("file")
    if not f:
        return Response({"detail": "请上传 PDF 文件"}, status=status.HTTP_400_BAD_REQUEST)
    # v0.5 存文件路径（生产环境用 MinIO）
    floor.floor_plan_file = f"floor_plans/floor_{floor.id}_{f.name}"
    floor.save()
    return Response({"detail": "上传成功", "floor_plan_file": floor.floor_plan_file})


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def floor_plan_data(request, floor_id: int):
    """F3-011/014: 平面图 JSON 获取与保存"""
    floor = get_object_or_404(Floor, pk=floor_id)
    if request.method == "PUT":
        floor.floor_plan_data = request.data.get("floor_plan_data", {})
        floor.save()
        return Response({
            "detail": "保存成功",
            "floor_plan_data": floor.floor_plan_data,
        })
    # GET
    return Response({
        "floor_id": floor.id,
        "floor_plan_file": floor.floor_plan_file,
        "floor_plan_data": floor.floor_plan_data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_rooms(request, floor_id: int):
    """F3-004: 查询未被方块关联的功能区域"""
    floor = get_object_or_404(Floor, pk=floor_id)
    all_rooms = Room.objects.filter(floor=floor)
    # 解析已关联的 room_id
    linked_ids = set()
    blocks = floor.floor_plan_data.get("blocks", [])
    for block in blocks:
        if block.get("room_id"):
            linked_ids.add(block["room_id"])
    available = [r for r in all_rooms if r.id not in linked_ids]
    return Response({"rooms": RoomSerializer(available, many=True).data})
