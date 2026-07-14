"""静态冷量计算结果模型（模块四，F4-001~050，PRD §15）

对齐数据库设计 PascalCase：
- RoomCalcResult：单房间计算全部中间值和最终值
- RoomLoadByWaterTemp：按水温分类（末端+新风分别记录，ADR-0001）
- LoadSummary：多级汇总（Room→Floor→Building+ExtraLoad→Project+ExtraLoad）
"""
from django.db import models


class RoomCalcResult(models.Model):
    """功能区域静态计算结果（一个区域一条记录，无 season）

    合并自 V1.0 的 room_load_result + room_air_volume_result（PRD §15）。
    """

    room = models.OneToOneField(
        "projects.Room", on_delete=models.CASCADE, related_name="calc_result",
        verbose_name="功能区域",
    )

    # ── 末端负荷中间结果（5 项，PRD §15.1，kW）──
    civil_load = models.DecimalField("土建负荷(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    lighting_load = models.DecimalField("照明负荷(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    personnel_load = models.DecimalField("人员负荷(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    electric_equipment_load = models.DecimalField("电动设备负荷(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    heated_equipment_load = models.DecimalField("电热设备负荷(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    terminal_load = models.DecimalField("末端负荷合计(kW)", max_digits=10, decimal_places=4)  # Q_terminal 桥梁

    # ── 风量结果（PRD §15.2）──
    total_exhaust_volume = models.DecimalField("总排风量(m³/h)", max_digits=12, decimal_places=2, null=True, blank=True)
    infiltration_air_volume = models.DecimalField("压差渗透风量(m³/h)", max_digits=12, decimal_places=2, null=True, blank=True)
    fresh_air_volume = models.DecimalField("新风量(m³/h)", max_digits=12, decimal_places=2, null=True, blank=True)

    # ── 焓值结果（PRD §15.3，psychrolib）──
    indoor_enthalpy_calc = models.DecimalField("室内焓值(kJ/kg)", max_digits=8, decimal_places=4, null=True, blank=True)
    outdoor_enthalpy_calc = models.DecimalField("室外焓值(kJ/kg)", max_digits=8, decimal_places=4, null=True, blank=True)
    enthalpy_diff = models.DecimalField("焓差(kJ/kg)", max_digits=8, decimal_places=4, null=True, blank=True)

    # ── 指标 ──
    cold_load_index = models.DecimalField("冷指标(W/m²)", max_digits=8, decimal_places=4, null=True, blank=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "RoomCalcResult"
        verbose_name = "功能区域计算结果"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.room.room_name} 计算结果"


class RoomLoadByWaterTemp(models.Model):
    """按水温分类的负荷结果（ADR-0001，末端+新风分别记录）

    一个房间在每种水温下一条记录。
    """

    room = models.ForeignKey(
        "projects.Room", on_delete=models.CASCADE, related_name="loads_by_water_temp",
        verbose_name="功能区域",
    )
    water_temp_config = models.ForeignKey(
        "common.WaterTempConfig", on_delete=models.PROTECT, related_name="room_loads",
        verbose_name="冷冻水温度档",
    )

    # 分别记录（PRD F4-023）
    terminal_load = models.DecimalField("末端负荷(kW)", max_digits=10, decimal_places=4, default=0)
    fresh_air_load = models.DecimalField("新风冷负荷(kW)", max_digits=10, decimal_places=4, default=0)  # 可为负
    total_load = models.DecimalField("总负荷(kW)", max_digits=10, decimal_places=4)  # <0 截断0

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "RoomLoadByWaterTemp"
        verbose_name = "按水温分类负荷"
        verbose_name_plural = verbose_name
        unique_together = [("room", "water_temp_config")]

    def __str__(self) -> str:
        return f"{self.room.room_name} @ {self.water_temp_config.temp_type_name}"


class LoadSummary(models.Model):
    """多级负荷汇总（PRD §15.6，scope: floor/building/project）"""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, verbose_name="项目")
    building = models.ForeignKey(
        "projects.Building", on_delete=models.CASCADE, null=True, blank=True, verbose_name="建筑（空=项目级）")
    floor = models.ForeignKey(
        "projects.Floor", on_delete=models.CASCADE, null=True, blank=True, verbose_name="楼层（空=建筑/项目级）")
    water_temp_config = models.ForeignKey(
        "common.WaterTempConfig", on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="水温档（空=汇总所有水温）")

    scope = models.CharField(  # 枚举
        "汇总层级", max_length=20,
        choices=[("floor", "楼层"), ("building", "建筑"), ("project", "项目")],
    )
    category = models.CharField("负荷类别", max_length=50)  # 新风负荷/末端负荷/PCW/.../合计

    fresh_air_load = models.DecimalField("新风冷负荷(kW)", max_digits=12, decimal_places=4, null=True, blank=True)
    terminal_load = models.DecimalField("末端负荷(kW)", max_digits=12, decimal_places=4, null=True, blank=True)
    extra_load = models.DecimalField("额外负荷(kW)", max_digits=12, decimal_places=4, null=True, blank=True)
    total_load = models.DecimalField("负荷合计(kW)", max_digits=12, decimal_places=4)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "LoadSummary"
        verbose_name = "负荷汇总"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.scope}/{self.category} {self.total_load}kW"
