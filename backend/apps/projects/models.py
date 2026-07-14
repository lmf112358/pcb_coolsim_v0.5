"""项目层级模型（模块一/二，F1/F2）

对齐数据库设计 PascalCase 表名 + Room 单表（PRD 附录 A，39 字段）：
- Project / Building / Floor / Room
- Room 是最小计算单元，负荷/风量/温湿度/新风/末端档全部直存（无子表）
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Project(models.Model):
    """项目/工厂（F1-015~023）"""

    project_name = models.CharField("项目名称", max_length=200)
    project_code = models.CharField("项目编号", max_length=50, blank=True)
    city = models.ForeignKey(
        "common.CityConfig", on_delete=models.PROTECT, related_name="projects",
        verbose_name="所属城市",
    )
    location = models.CharField("详细地址", max_length=200, blank=True)
    description = models.TextField("项目描述", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "Project"
        verbose_name = "项目"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.project_name


class Building(models.Model):
    """建筑（F2-009~011）"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="buildings",
        verbose_name="所属项目",
    )
    building_name = models.CharField("建筑名称", max_length=100)
    building_code = models.CharField("建筑编号", max_length=50, blank=True)
    description = models.CharField("建筑描述", max_length=500, blank=True)
    sort_order = models.IntegerField("排序", default=0)  # F2-003 拖拽排序
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "Building"
        verbose_name = "建筑"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.building_name


class Floor(models.Model):
    """楼层（F2-012~013）

    floor_plan_file：底图 PDF 路径（F3-001/013，MinIO 存储）
    floor_plan_data：平面图 JSON（F3-011，外墙/方块/比例尺/指北针，PRD §7.4）
    """

    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="floors",
        verbose_name="所属建筑",
    )
    floor_name = models.CharField("楼层名称", max_length=50)
    floor_area = models.DecimalField("楼层面积(m²)", max_digits=12, decimal_places=2, null=True, blank=True)
    floor_height = models.DecimalField("层高(m)", max_digits=5, decimal_places=2, null=True, blank=True)
    floor_plan_file = models.CharField("底图PDF路径", max_length=500, blank=True)
    floor_plan_data = models.JSONField("平面图数据", default=dict, blank=True)
    sort_order = models.IntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "Floor"
        verbose_name = "楼层"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.building.building_name} {self.floor_name}"


class Room(models.Model):
    """功能区域（最小计算单元，PRD §6.5 + 附录 A，单表 39 字段）

    v0.5.1 合并：负荷/风量/温湿度/新风/末端档全部直存（删除子表）。
    ADR-0001：末端负荷按 terminal_water_temp_config_id 归档（默认中温）。
    """

    floor = models.ForeignKey(
        Floor, on_delete=models.CASCADE, related_name="rooms",
        verbose_name="所属楼层",
    )

    # ── 基本信息 ──
    room_name = models.CharField("功能区域名称", max_length=100)
    room_code = models.CharField("功能区域编号", max_length=50, blank=True)
    area = models.DecimalField("面积(m²)", max_digits=10, decimal_places=2)
    height = models.DecimalField("吊顶高度(m)", max_digits=5, decimal_places=2)
    volume = models.DecimalField("体积(m³)", max_digits=12, decimal_places=2, blank=True, null=True)  # 自动=area×height

    # ── 温湿度要求（F2-014，第二组）──
    design_temp_requirement = models.CharField("设计温度要求", max_length=50, blank=True)
    design_humidity_requirement = models.CharField("设计相对湿度要求", max_length=50, blank=True)
    temp_precision = models.CharField(  # 枚举，工艺色编码最高优先级（F3-016）
        "温控精度", max_length=10, blank=True,
        choices=[("±1", "±1"), ("±2", "±2"), ("±3", "±3"), ("±5", "±5"), ("none", "无要求")],
    )
    indoor_calc_temp = models.DecimalField("室内计算温度(℃)", max_digits=5, decimal_places=2, null=True, blank=True)  # 空取26
    indoor_calc_humidity = models.DecimalField("室内计算相对湿度(%)", max_digits=5, decimal_places=2, null=True, blank=True)  # 空取55
    cleanliness_level = models.CharField("洁净度等级", max_length=50, blank=True)

    # ── 负荷计算参数（F2-014，第三/四组）──
    civil_load_index = models.DecimalField("土建指标(W/m²)", max_digits=8, decimal_places=4)
    lighting_load_index = models.DecimalField("照明指标(W/m²)", max_digits=8, decimal_places=4)
    personnel_load_index = models.DecimalField("人员指标(W/人)", max_digits=8, decimal_places=4, null=True, blank=True)  # 空取0
    personnel_count = models.IntegerField("人数", null=True, blank=True)  # 空取0
    electric_equipment_power = models.DecimalField("电动设备功率(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    electric_equipment_coefficient = models.DecimalField("电动设备系数", max_digits=5, decimal_places=4, null=True, blank=True)
    heated_equipment_power_with_exhaust = models.DecimalField("有排风电热功率(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    heated_equipment_coefficient_with_exhaust = models.DecimalField("有排风电热系数", max_digits=5, decimal_places=4, null=True, blank=True)
    heated_equipment_power_without_exhaust = models.DecimalField("无排风电热功率(kW)", max_digits=10, decimal_places=4, null=True, blank=True)
    heated_equipment_coefficient_without_exhaust = models.DecimalField("无排风电热系数", max_digits=5, decimal_places=4, null=True, blank=True)

    # ── 风量参数（F2-014，第五组）──
    heat_exhaust_volume = models.DecimalField("热排风量(m³/h)", max_digits=10, decimal_places=2, null=True, blank=True)
    acid_exhaust_volume = models.DecimalField("酸性排风量(m³/h)", max_digits=10, decimal_places=2, null=True, blank=True)
    alkali_exhaust_volume = models.DecimalField("碱性排风量(m³/h)", max_digits=10, decimal_places=2, null=True, blank=True)
    organic_exhaust_volume = models.DecimalField("有机排风量(m³/h)", max_digits=10, decimal_places=2, null=True, blank=True)
    dust_exhaust_volume = models.DecimalField("含尘排风量(m³/h)", max_digits=10, decimal_places=2, null=True, blank=True)
    total_exhaust_volume = models.DecimalField("总排风量(m³/h)", max_digits=12, decimal_places=2, blank=True, null=True)  # 自动=五类之和
    pressure_diff = models.DecimalField("功能区域压差(Pa)", max_digits=5, decimal_places=2, null=True, blank=True)
    air_change_rate = models.IntegerField("设计换气次数(次/h)", null=True, blank=True)  # v0.5 不参与计算
    supply_air_temp_diff = models.DecimalField("送风温差(℃)", max_digits=5, decimal_places=2, null=True, blank=True)  # v0.5 不参与计算

    # ── 新风处理配置（F2-014，第六组）──
    fresh_air_water_mode = models.CharField(  # 枚举
        "新风冷冻水模式", max_length=10, blank=True, default="single",
        choices=[("single", "单水温模式"), ("dual", "两阶段模式")],
    )
    fresh_air_water_temp_config = models.ForeignKey(
        "common.WaterTempConfig", on_delete=models.SET_NULL, related_name="+",
        verbose_name="单水温档/第一段档", null=True, blank=True,
    )
    fresh_air_water_temp_config_2 = models.ForeignKey(
        "common.WaterTempConfig", on_delete=models.SET_NULL, related_name="+",
        verbose_name="两阶段第二段档", null=True, blank=True,
    )

    # ── 末端冷冻水档（ADR-0001，第七组）──
    terminal_water_temp_config = models.ForeignKey(
        "common.WaterTempConfig", on_delete=models.SET_NULL, related_name="terminal_rooms",
        verbose_name="末端冷冻水档", null=True, blank=True,
        help_text="末端负荷归属的冷冻水档，空=中温默认（ADR-0001）",
    )

    # ── 状态 ──
    status = models.CharField(  # 对话采集草稿态（ADR-0007）
        "状态", max_length=10, default="active",
        choices=[("draft", "草稿"), ("active", "已确认")],
    )
    description = models.CharField("描述", max_length=500, blank=True)
    sort_order = models.IntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "Room"
        verbose_name = "功能区域"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.room_name

    def clean(self) -> None:
        """校验：面积/高度为正"""
        if self.area is not None and self.area <= 0:
            raise ValidationError({"area": "面积必须大于 0"})
        if self.height is not None and self.height <= 0:
            raise ValidationError({"height": "吊顶高度必须大于 0"})

    def save(self, *args, **kwargs):
        """自动计算 volume 与 total_exhaust_volume（PRD §15）"""
        if self.area and self.height:
            self.volume = (self.area * self.height).quantize(Decimal("0.01"))
        self.total_exhaust_volume = sum(filter(None, [
            self.heat_exhaust_volume, self.acid_exhaust_volume,
            self.alkali_exhaust_volume, self.organic_exhaust_volume,
            self.dust_exhaust_volume,
        ]), Decimal("0"))
        super().save(*args, **kwargs)


class ExtraLoad(models.Model):
    """额外负荷（F2-027~031，building_id 区分层级）"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="extra_loads",
        verbose_name="所属项目",
    )
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="extra_loads", null=True, blank=True,
        verbose_name="所属建筑（空=项目级）",
    )
    category = models.CharField(  # 枚举
        "负荷类别", max_length=50,
        choices=[
            ("PCW", "PCW"), ("配电室空调", "配电室空调"), ("工艺热水", "工艺热水"),
            ("消防池保温", "消防池保温"), ("消防池护层", "消防池护层"), ("其他", "其他"),
        ],
    )
    load_value = models.DecimalField("负荷值(kW)", max_digits=12, decimal_places=4)
    water_temp_config = models.ForeignKey(
        "common.WaterTempConfig", on_delete=models.SET_NULL, related_name="+",
        verbose_name="关联冷冻水分类", null=True, blank=True,
    )
    description = models.CharField("备注", max_length=200, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "ExtraLoad"
        verbose_name = "额外负荷"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        loc = self.building.building_name if self.building else "项目级"
        return f"{loc} {self.category} {self.load_value}kW"
