"""气象数据 services（F4-043~050）

- parse_weather_csv：CSV 上传解析
- check_weather_quality：质量检查（缺失检测、时间连续性）
- get_weather_summary：数据概览
"""
import csv
import io
from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone

from .models import WeatherRecord


def parse_weather_csv(csv_bytes: bytes, city) -> dict:
    """解析 CSV 气象数据（F4-050）

    格式：timestamp,dry_bulb_temp,wet_bulb_temp,humidity[,pressure,wind_speed]
    """
    text = csv_bytes.decode("utf-8-sig")  # 兼容 BOM
    reader = csv.DictReader(io.StringIO(text))
    records = []
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            ts = datetime.fromisoformat(row["timestamp"].strip())
            record = WeatherRecord(
                city=city,
                timestamp=ts,
                dry_bulb_temp=Decimal(row["dry_bulb_temp"]) if row.get("dry_bulb_temp") else None,
                wet_bulb_temp=Decimal(row["wet_bulb_temp"]) if row.get("wet_bulb_temp") else None,
                humidity=Decimal(row["humidity"]) if row.get("humidity") else None,
                atmospheric_pressure=Decimal(row["pressure"]) if row.get("pressure") else None,
                wind_speed=Decimal(row["wind_speed"]) if row.get("wind_speed") else None,
                source="manual",
            )
            records.append(record)
        except (KeyError, ValueError) as e:
            errors.append({"row": i, "error": str(e)})

    if not records:
        return {"success": False, "error_count": len(errors), "errors": errors,
                "message": "无有效记录"}

    # 批量写入（update_or_create 避免重复）
    created = 0
    for r in records:
        _, was_created = WeatherRecord.objects.update_or_create(
            city=r.city, timestamp=r.timestamp,
            defaults={
                "dry_bulb_temp": r.dry_bulb_temp,
                "wet_bulb_temp": r.wet_bulb_temp,
                "humidity": r.humidity,
                "atmospheric_pressure": r.atmospheric_pressure,
                "wind_speed": r.wind_speed,
                "source": r.source,
            },
        )
        if was_created:
            created += 1

    return {
        "success": True,
        "created_count": created,
        "total_parsed": len(records),
        "error_count": len(errors),
        "errors": errors,
    }


def check_weather_quality(city) -> dict:
    """F4-044: 数据质量检查（缺失检测、时间连续性）"""
    records = list(WeatherRecord.objects.filter(city=city).order_by("timestamp"))
    if len(records) < 2:
        return {"record_count": len(records), "missing_count": 0, "gaps": []}

    missing_count = 0
    gaps = []
    for i in range(1, len(records)):
        delta = records[i].timestamp - records[i - 1].timestamp
        expected = timedelta(hours=1)
        if delta > expected:
            gap_hours = int(delta.total_seconds() / 3600) - 1
            missing_count += gap_hours
            gaps.append({
                "from": records[i - 1].timestamp.isoformat(),
                "to": records[i].timestamp.isoformat(),
                "missing_hours": gap_hours,
            })

    # 缺失值统计
    null_fields = {}
    for field in ["dry_bulb_temp", "wet_bulb_temp", "humidity"]:
        null_count = sum(1 for r in records if getattr(r, field) is None)
        if null_count > 0:
            null_fields[field] = null_count

    return {
        "record_count": len(records),
        "missing_count": missing_count,
        "gaps": gaps,
        "null_fields": null_fields,
    }


def get_weather_summary(city) -> dict:
    """F4-048: 气象数据概览"""
    records = WeatherRecord.objects.filter(city=city).order_by("timestamp")
    count = records.count()
    if count == 0:
        return {
            "city": city.city_name,
            "record_count": 0,
            "time_range_start": None,
            "time_range_end": None,
            "temp_range": None,
            "source": None,
        }

    first = records.first()
    last = records.last()
    temps = [r.dry_bulb_temp for r in records if r.dry_bulb_temp is not None]
    sources = set(records.values_list("source", flat=True))

    return {
        "city": city.city_name,
        "record_count": count,
        "time_range_start": first.timestamp.isoformat() if first else None,
        "time_range_end": last.timestamp.isoformat() if last else None,
        "temp_range": {
            "min": str(min(temps)) if temps else None,
            "max": str(max(temps)) if temps else None,
        },
        "source": list(sources),
    }
