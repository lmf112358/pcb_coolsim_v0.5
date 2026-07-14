"""负荷预测模型（模块十 F10，PRD §14）

对齐数据库设计 PascalCase：
- ForecastScenario：预测场景（active/paused/archived）
- ForecastWeatherData：预测天气（逐时168点）
- ForecastProductionRate：生产负荷率（多段）
- ForecastHourlyResult：预测逐时结果（含历史版本）
- RatioCoefficient：比例系数表（ADR-0003 统一权威表）
"""
from django.db import models


class ForecastScenario(models.Model):
    """预测场景（F10-001~004）"""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="forecast_scenarios",
        verbose_name="所属项目",
    )
    name = models.CharField("场景名称", max_length=100)
    start_date = models.DateField("开始日期")
    weather_source = models.CharField(
        "天气来源", max_length=10, default="api",
        choices=[("api", "API 自动"), ("manual", "手动上传")],
    )
    status = models.CharField(
        "状态", max_length=10, default="active",
        choices=[("active", "活跃"), ("paused", "暂停"), ("archived", "归档")],
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "ForecastScenario"
        verbose_name = "预测场景"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.project.project_name} - {self.name}"


class ForecastWeatherData(models.Model):
    """预测天气数据（逐时，168点，F10-005~010）"""

    scenario = models.ForeignKey(
        ForecastScenario, on_delete=models.CASCADE, related_name="weather_data",
        verbose_name="所属场景",
    )
    timestamp = models.DateTimeField("时刻")
    temp_dry = models.DecimalField("干球温度(℃)", max_digits=5, decimal_places=2)
    humidity = models.DecimalField("相对湿度(%)", max_digits=5, decimal_places=2, null=True, blank=True)
    source = models.CharField("来源", max_length=10, default="api")
    fetched_at = models.DateTimeField("抓取时间", auto_now_add=True)

    class Meta:
        db_table = "ForecastWeatherData"
        verbose_name = "预测天气"
        verbose_name_plural = verbose_name
        ordering = ["timestamp"]


class ForecastProductionRate(models.Model):
    """生产负荷率配置（多段，F10-011~013）"""

    scenario = models.ForeignKey(
        ForecastScenario, on_delete=models.CASCADE, related_name="production_rates",
        verbose_name="所属场景",
    )
    rate_value = models.DecimalField("负荷率(%)", max_digits=5, decimal_places=2)
    duration_hours = models.IntegerField("持续时长(小时)")
    sort_order = models.IntegerField("排序", default=0)

    class Meta:
        db_table = "ForecastProductionRate"
        verbose_name = "生产负荷率"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]


class ForecastHourlyResult(models.Model):
    """预测逐时结果（功能区域级，含历史版本，F10-017~020）"""

    scenario = models.ForeignKey(
        ForecastScenario, on_delete=models.CASCADE, related_name="hourly_results",
        verbose_name="所属场景",
    )
    room = models.ForeignKey(
        "projects.Room", on_delete=models.CASCADE, related_name="forecast_results",
        verbose_name="功能区域",
    )
    timestamp = models.DateTimeField("时刻")
    outdoor_temp = models.DecimalField("室外温度(℃)", max_digits=5, decimal_places=2)
    ratio_coefficient = models.DecimalField("比例系数 K", max_digits=8, decimal_places=4)
    predicted_load = models.DecimalField("预测负荷(kW)", max_digits=12, decimal_places=4)
    fetched_at = models.DateTimeField("计算批次时间", auto_now_add=True)

    class Meta:
        db_table = "ForecastHourlyResult"
        verbose_name = "预测逐时结果"
        verbose_name_plural = verbose_name
        ordering = ["timestamp"]


class RatioCoefficient(models.Model):
    """比例系数表（ADR-0003 统一权威表，PRD §14.8）

    维度：温度区间 × 负荷率 → 系数 K。
    动态仿真方式二取负荷率=100% 列；负荷预测用全表（双线性插值）。
    """

    temp_min = models.DecimalField("温度区间下限(℃)", max_digits=5, decimal_places=2)
    temp_max = models.DecimalField("温度区间上限(℃)", max_digits=5, decimal_places=2)
    rate_percent = models.IntegerField("负荷率(%)")  # 10/30/50/80/100
    coefficient = models.DecimalField("系数 K", max_digits=6, decimal_places=4)
    is_default = models.BooleanField("是否系统默认", default=True)
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="ratio_coefficients",
        verbose_name="项目级覆盖", null=True, blank=True,
    )

    class Meta:
        db_table = "RatioCoefficient"
        verbose_name = "比例系数"
        verbose_name_plural = verbose_name
        unique_together = [("temp_min", "temp_max", "rate_percent", "project")]

    def __str__(self) -> str:
        return f"{self.temp_min}~{self.temp_max}℃ @ {self.rate_percent}% → K={self.coefficient}"
