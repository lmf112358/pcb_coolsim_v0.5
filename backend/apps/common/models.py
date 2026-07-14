"""公共配置模型

对齐数据库设计 PascalCase 表名：
- CityConfig：城市配置/国标参数（PRD F4-038~042，约300城市只读）
- WaterTempConfig：冷冻水温度配置（项目级，F9-001~005）
- DefaultConfig：默认值四级继承（F2-040~045/F9-006~010）
"""
from django.db import models


class CityConfig(models.Model):
    """城市配置（系统预置，国标室外设计参数，F4-038~042）

    系统部署时从国标 Excel 批量导入约 300 城市，用户只读。
    """

    # 城市基础信息
    city_name = models.CharField("城市名称", max_length=50)
    province = models.CharField("省份", max_length=50, blank=True)
    station_name = models.CharField("台站名称", max_length=100, blank=True)
    station_code = models.CharField("台站编号", max_length=20, blank=True)
    latitude = models.CharField("纬度", max_length=20, blank=True)
    longitude = models.CharField("经度", max_length=20, blank=True)
    altitude = models.DecimalField("海拔(m)", max_digits=8, decimal_places=2, null=True, blank=True)
    statistical_years = models.CharField("统计年份", max_length=50, blank=True)

    # 大气压力（hPa）—— 焓值计算入参（PRD 附录 C 12 参数）
    pressure_winter = models.DecimalField("冬季大气压力(hPa)", max_digits=8, decimal_places=1, null=True, blank=True)
    pressure_summer = models.DecimalField("夏季大气压力(hPa)", max_digits=8, decimal_places=1, null=True, blank=True)

    # 风速
    wind_speed_winter = models.DecimalField("冬季风速(m/s)", max_digits=4, decimal_places=1, null=True, blank=True)
    wind_speed_summer = models.DecimalField("夏季风速(m/s)", max_digits=4, decimal_places=1, null=True, blank=True)

    # 夏季空调参数（焓值计算核心，PRD F4-039）
    temp_dry_ac_summer = models.DecimalField("夏季空调干球温度(℃)", max_digits=5, decimal_places=1, null=True, blank=True)
    temp_wet_ac_summer = models.DecimalField("夏季空调湿球温度(℃)", max_digits=5, decimal_places=1, null=True, blank=True)

    # 冬季参数（v0.6 预留）
    temp_dry_ac_winter = models.DecimalField("冬季空调干球温度(℃)", max_digits=5, decimal_places=1, null=True, blank=True)
    humidity_ac_winter = models.DecimalField("冬季空调相对湿度(%)", max_digits=5, decimal_places=1, null=True, blank=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "CityConfig"
        verbose_name = "城市配置"
        verbose_name_plural = verbose_name
        ordering = ["province", "city_name"]

    def __str__(self) -> str:
        return f"{self.province} {self.city_name}"


class WaterTempConfig(models.Model):
    """冷冻水温度配置（项目级，F9-001~005）

    系统预置：低温 7/12°C、中温 12/17°C（F1-018 项目创建时自动生成）。
    """

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="water_temp_configs",
        verbose_name="所属项目",
    )
    temp_type_name = models.CharField("配置名称", max_length=50)  # 如"低温冷冻水"
    supply_temp = models.DecimalField("供水温度(℃)", max_digits=5, decimal_places=2)
    return_temp = models.DecimalField("回水温度(℃)", max_digits=5, decimal_places=2)
    description = models.CharField("备注", max_length=200, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "WaterTempConfig"
        verbose_name = "冷冻水温度配置"
        verbose_name_plural = verbose_name
        unique_together = [("project", "temp_type_name")]

    def __str__(self) -> str:
        return f"{self.temp_type_name} {self.supply_temp}/{self.return_temp}°C"
