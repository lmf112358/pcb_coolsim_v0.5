# PCB-CoolSim API 设计规范

> 版本: 1.0
> 日期: 2026-07-09
> 状态: 草稿
> 基础 URL: /api/v1

---

## 1. API 概述

### 1.1 设计原则

- **RESTful:** 资源即名词，HTTP 方法即动词
- **Versioned:** URL 路径版本控制（`/api/v1/`）
- **Consistent:** 所有端点响应格式统一
- **Secure:** JWT 认证，基于角色的授权
- **Documented:** OpenAPI 3.0 规范

### 1.2 通用请求头

```
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
X-Request-ID: {uuid} (可选，用于链路追踪)
```

### 1.3 通用响应状态码

| 状态码 | 含义 | 使用场景 |
|------|---------|-------|
| 200 | 成功 | GET、PUT 成功 |
| 201 | 已创建 | POST 成功 |
| 204 | 无内容 | DELETE 成功 |
| 400 | 请求错误 | 校验错误 |
| 401 | 未授权 | 令牌无效或缺失 |
| 403 | 禁止 | 权限不足 |
| 404 | 未找到 | 资源不存在 |
| 409 | 冲突 | 资源重复 |
| 422 | 不可处理实体 | 业务逻辑错误 |
| 500 | 服务器内部错误 | 服务器错误 |

---

## 2. 认证 API

### 2.1 登录

**POST** `/api/v1/auth/login/`

**请求：**
```json
{
  "username": "engineer@example.com",
  "password": "secure_password"
}
```

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": 1,
      "username": "engineer@example.com",
      "email": "engineer@example.com",
      "role": "engineer",
      "full_name": "John Doe"
    }
  }
}
```

**错误 (401)：**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password"
  }
}
```

### 2.2 刷新令牌

**POST** `/api/v1/auth/refresh/`

**请求：**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900
  }
}
```

### 2.3 登出

**POST** `/api/v1/auth/logout/`

**请求：**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应 (204)：** 无内容

---

## 3. 项目 API

### 3.1 项目列表

**GET** `/api/v1/projects/`

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| page | integer | 否 | 页码（默认：1） |
| page_size | integer | 否 | 每页条数（默认：20，最大：100） |
| search | string | 否 | 按名称或编码搜索 |
| status | string | 否 | 按状态筛选（active、archived） |

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "project_name": "上海松江 AI 服务器 PCB 工厂",
        "project_code": "SH-SJ-2026-001",
        "city": {
          "id": 1,
          "city_name": "上海",
          "province": "上海"
        },
        "location": "松江区XX路XX号",
        "building_count": 3,
        "total_cooling_load": 15000.5,
        "status": "active",
        "created_at": "2026-07-01T10:00:00Z",
        "updated_at": "2026-07-09T15:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

### 3.2 创建项目

**POST** `/api/v1/projects/`

**请求：**
```json
{
  "project_name": "深圳宝安 PCB 工厂",
  "project_code": "SZ-BA-2026-001",
  "city_id": 2,
  "location": "宝安区XX街道XX号",
  "description": "大型PCB制造工厂"
}
```

**响应 (201)：**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "project_name": "深圳宝安 PCB 工厂",
    "project_code": "SZ-BA-2026-001",
    "city": {
      "id": 2,
      "city_name": "深圳",
      "province": "广东"
    },
    "location": "宝安区XX街道XX号",
    "description": "大型PCB制造工厂",
    "water_temperature_configs": [
      {
        "id": 1,
        "name": "低温",
        "supply_temp": 7,
        "return_temp": 12
      },
      {
        "id": 2,
        "name": "中温",
        "supply_temp": 12,
        "return_temp": 17
      }
    ],
    "created_at": "2026-07-09T16:00:00Z"
  }
}
```

### 3.3 获取项目详情

**GET** `/api/v1/projects/{id}/`

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "project_name": "上海松江 AI 服务器 PCB 工厂",
    "project_code": "SH-SJ-2026-001",
    "city": {
      "id": 1,
      "city_name": "上海",
      "province": "上海",
      "outdoor_temp_summer": 34.6,
      "outdoor_humidity_summer": 75
    },
    "location": "松江区XX路XX号",
    "description": "大型AI服务器PCB制造工厂",
    "buildings": [
      {
        "id": 1,
        "building_name": "1#厂房",
        "floor_count": 3,
        "room_count": 45
      }
    ],
    "water_temperature_configs": [...],
    "weather_data_status": "available",
    "last_static_calculation": "2026-07-09T14:00:00Z",
    "created_at": "2026-07-01T10:00:00Z",
    "updated_at": "2026-07-09T15:30:00Z"
  }
}
```

### 3.4 更新项目

**PUT** `/api/v1/projects/{id}/`

**请求：**
```json
{
  "project_name": "上海松江 AI 服务器 PCB 工厂（二期）",
  "location": "松江区XX路XX号（更新地址）"
}
```

**响应 (200)：** 同「获取项目详情」

### 3.5 删除项目

**DELETE** `/api/v1/projects/{id}/`

**响应 (204)：** 无内容

### 3.6 获取项目汇总

**GET** `/api/v1/projects/{id}/summary/`

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "project_id": 1,
    "total_buildings": 3,
    "total_floors": 9,
    "total_rooms": 135,
    "cooling_load_summary": {
      "total_load_kw": 15000.5,
      "by_water_temperature": {
        "low_temp_7_12": 5000.2,
        "mid_temp_12_17": 10000.3
      },
      "by_building": [
        {
          "building_id": 1,
          "building_name": "1#厂房",
          "load_kw": 8000.0
        }
      ]
    },
    "simulation_status": "completed",
    "last_simulation_date": "2026-07-09T14:00:00Z"
  }
}
```

---

## 4. 建筑 API

### 4.1 建筑列表

**GET** `/api/v1/buildings/?project={project_id}`

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| project | integer | 是 | 项目 ID |
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页条数 |

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "building_name": "1#厂房",
        "building_code": "B001",
        "description": "主生产厂房",
        "floor_count": 3,
        "room_count": 45,
        "created_at": "2026-07-01T10:00:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

### 4.2 创建建筑

**POST** `/api/v1/buildings/`

**请求：**
```json
{
  "project_id": 1,
  "building_name": "2#厂房",
  "building_code": "B002",
  "description": "二期生产厂房"
}
```

**响应 (201)：**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "project_id": 1,
    "building_name": "2#厂房",
    "building_code": "B002",
    "description": "二期生产厂房",
    "created_at": "2026-07-09T16:00:00Z"
  }
}
```

---

## 5. 楼层 API

### 5.1 楼层列表

**GET** `/api/v1/floors/?building={building_id}`

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "floor_name": "1F",
        "room_count": 15,
        "created_at": "2026-07-01T10:00:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

### 5.2 创建楼层

**POST** `/api/v1/floors/`

**请求：**
```json
{
  "building_id": 1,
  "floor_name": "2F"
}
```

---

## 6. 房间 API

### 6.1 房间列表

**GET** `/api/v1/rooms/?floor={floor_id}`

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| floor | integer | 是 | 楼层 ID |
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页条数 |
| search | string | 否 | 按名称或编码搜索 |

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "room_name": "内层曝光区",
        "room_code": "R001",
        "area": 500.00,
        "height": 4.50,
        "volume": 2250.00,
        "indoor_calc_temp": 23.00,
        "indoor_calc_humidity": 55.00,
        "cleanliness_level": "ISO7",
        "water_tier": "mid_temp",
        "has_calculation": true,
        "last_calculation_date": "2026-07-09T14:00:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

### 6.2 创建房间

**POST** `/api/v1/rooms/`

**请求：**
```json
{
  "floor_id": 1,
  "room_name": "电镀车间",
  "room_code": "R002",
  "area": 800.00,
  "height": 5.00,
  "design_temp_requirement": "25±2",
  "design_humidity_requirement": "50±10",
  "indoor_calc_temp": 25.00,
  "indoor_calc_humidity": 50.00,
  "cleanliness_level": null,
  "water_tier_id": 2,
  "load_parameters": {
    "civil_load_index": 50.00,
    "lighting_load_index": 20.00,
    "personnel_load_index": 120.00,
    "personnel_count": 20,
    "electric_equipment_power": 100.00,
    "electric_equipment_factor": 0.7,
    "exhaust_heated_equipment_power": 50.00,
    "exhaust_heated_equipment_factor": 0.8
  },
  "air_volume_parameters": {
    "heat_exhaust_volume": 2000.00,
    "acid_exhaust_volume": 500.00,
    "pressure_diff": 15.00
  }
}
```

**响应 (201)：**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "room_name": "电镀车间",
    "room_code": "R002",
    "area": 800.00,
    "height": 5.00,
    "volume": 4000.00,
    "load_parameters": {...},
    "air_volume_parameters": {...},
    "created_at": "2026-07-09T16:00:00Z"
  }
}
```

### 6.3 获取房间详情

**GET** `/api/v1/rooms/{id}/`

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "room_name": "内层曝光区",
    "room_code": "R001",
    "floor_id": 1,
    "floor_name": "1F",
    "building_id": 1,
    "building_name": "1#厂房",
    "project_id": 1,
    "area": 500.00,
    "height": 4.50,
    "volume": 2250.00,
    "design_temp_requirement": "23±2",
    "design_humidity_requirement": "55±5",
    "indoor_calc_temp": 23.00,
    "indoor_calc_humidity": 55.00,
    "cleanliness_level": "ISO7",
    "water_tier": {
      "id": 2,
      "name": "中温",
      "supply_temp": 12,
      "return_temp": 17
    },
    "load_parameters": {
      "civil_load_index": 45.00,
      "lighting_load_index": 18.00,
      "personnel_load_index": 120.00,
      "personnel_count": 15,
      "electric_equipment_power": 80.00,
      "electric_equipment_factor": 0.8,
      "exhaust_heated_equipment_power": 30.00,
      "exhaust_heated_equipment_factor": 0.7,
      "no_exhaust_heated_equipment_power": 20.00,
      "no_exhaust_heated_equipment_factor": 0.6
    },
    "air_volume_parameters": {
      "heat_exhaust_volume": 1500.00,
      "acid_exhaust_volume": 300.00,
      "alkaline_exhaust_volume": 0,
      "organic_exhaust_volume": 200.00,
      "dust_exhaust_volume": 0,
      "total_exhaust_volume": 2000.00,
      "pressure_diff": 15.00,
      "design_ach": 6,
      "supply_temp_diff": 10.00
    },
    "created_at": "2026-07-01T10:00:00Z",
    "updated_at": "2026-07-09T14:00:00Z"
  }
}
```

### 6.4 更新房间

**PUT** `/api/v1/rooms/{id}/`

**请求：** 同「创建房间」（支持部分更新）

### 6.5 删除房间

**DELETE** `/api/v1/rooms/{id}/`

**响应 (204)：** 无内容

---

## 7. 计算 API

### 7.1 计算静态负荷（单房间）

**POST** `/api/v1/rooms/{id}/calculate-static/`

**请求：** 无需请求体（使用当前房间参数）

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "room_id": 1,
    "calculation_date": "2026-07-09T14:00:00Z",
    "steps": {
      "step1_enthalpy": {
        "indoor_enthalpy": 52.34,
        "outdoor_enthalpy": 90.12,
        "enthalpy_diff": 37.78,
        "status": "success"
      },
      "step2_terminal_load": {
        "civil_load": 22500.00,
        "lighting_load": 9000.00,
        "personnel_load": 1800.00,
        "electric_equipment_load": 51200.00,
        "exhaust_heated_equipment_load": 16800.00,
        "no_exhaust_heated_equipment_load": 12000.00,
        "terminal_load": 113300.00,
        "status": "success"
      },
      "step3_air_volume": {
        "total_exhaust_volume": 2000.00,
        "infiltration_volume": 450.00,
        "fresh_air_volume": 2450.00,
        "supply_air_volume": 15000.00,
        "return_air_volume": 12550.00,
        "status": "success"
      },
      "step4_fresh_air_load": {
        "fresh_air_load": 92561.00,
        "water_tier": "mid_temp",
        "status": "success"
      },
      "step5_total_load": {
        "terminal_load": 113300.00,
        "fresh_air_load": 92561.00,
        "total_load": 205861.00,
        "status": "success"
      }
    },
    "summary": {
      "terminal_load_kw": 113.30,
      "fresh_air_load_kw": 92.56,
      "total_load_kw": 205.86,
      "load_density_w_m2": 411.72
    },
    "warnings": []
  }
}
```

### 7.2 计算静态负荷（批量）

**POST** `/api/v1/projects/{id}/calculate-static/`

**请求：**
```json
{
  "building_ids": [1, 2],
  "floor_ids": null,
  "room_ids": null,
  "recalculate_all": false
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "task_id": "calc-static-20260709-001",
    "status": "processing",
    "message": "Static calculation started for 90 rooms",
    "websocket_url": "ws://localhost:8000/ws/tasks/calc-static-20260709-001/"
  }
}
```

### 7.3 获取静态计算结果

**GET** `/api/v1/calculations/static/{project_id}/`

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| building_id | integer | 否 | 按建筑筛选 |
| floor_id | integer | 否 | 按楼层筛选 |
| water_tier_id | integer | 否 | 按水温梯度筛选 |

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "project_id": 1,
    "calculation_date": "2026-07-09T14:00:00Z",
    "summary": {
      "total_rooms": 135,
      "calculated_rooms": 130,
      "skipped_rooms": 5,
      "total_load_kw": 15000.50,
      "by_water_tier": {
        "low_temp_7_12": {
          "load_kw": 5000.20,
          "room_count": 40
        },
        "mid_temp_12_17": {
          "load_kw": 10000.30,
          "room_count": 90
        }
      }
    },
    "buildings": [
      {
        "building_id": 1,
        "building_name": "1#厂房",
        "total_load_kw": 8000.00,
        "floors": [
          {
            "floor_id": 1,
            "floor_name": "1F",
            "total_load_kw": 3000.00,
            "rooms": [
              {
                "room_id": 1,
                "room_name": "内层曝光区",
                "terminal_load_kw": 113.30,
                "fresh_air_load_kw": 92.56,
                "total_load_kw": 205.86,
                "water_tier": "mid_temp"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 7.4 运行动态仿真

**POST** `/api/v1/projects/{id}/simulate/`

**请求：**
```json
{
  "simulation_type": "weather_driven",
  "years": 3,
  "start_date": "2023-01-01",
  "building_ids": null,
  "room_ids": null
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "task_id": "sim-dynamic-20260709-001",
    "status": "processing",
    "message": "Dynamic simulation started (8760h × 3 years × 135 rooms)",
    "estimated_time_seconds": 25,
    "websocket_url": "ws://localhost:8000/ws/tasks/sim-dynamic-20260709-001/"
  }
}
```

### 7.5 获取仿真结果

**GET** `/api/v1/calculations/dynamic/{project_id}/`

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| room_id | integer | 否 | 按房间筛选 |
| year | integer | 否 | 按年份筛选 |
| month | integer | 否 | 按月份筛选 |
| aggregation | string | 否 | hourly、daily、monthly |

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "project_id": 1,
    "simulation_type": "weather_driven",
    "simulation_date": "2026-07-09T14:00:00Z",
    "years_simulated": 3,
    "summary": {
      "max_load_kw": 18000.50,
      "max_load_datetime": "2024-07-15T14:00:00Z",
      "min_load_kw": 2000.30,
      "min_load_datetime": "2024-01-20T06:00:00Z",
      "avg_load_kw": 8500.20,
      "total_energy_kwh": 223260000
    },
    "room_results": [
      {
        "room_id": 1,
        "room_name": "内层曝光区",
        "max_load_kw": 250.50,
        "min_load_kw": 50.20,
        "avg_load_kw": 150.30,
        "hourly_data": [
          {
            "datetime": "2023-01-01T00:00:00Z",
            "outdoor_temp": 5.20,
            "outdoor_humidity": 75.00,
            "load_kw": 120.50
          }
        ]
      }
    ]
  }
}
```

---

## 8. 气象 API

### 8.1 获取气象数据

**GET** `/api/v1/weather/?city={city_id}`

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| city | integer | 是 | 城市 ID |
| year | integer | 否 | 按年份筛选 |
| start_date | string | 否 | 开始日期（YYYY-MM-DD） |
| end_date | string | 否 | 结束日期（YYYY-MM-DD） |

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "city_id": 1,
    "city_name": "上海",
    "data_years": [2023, 2024, 2025],
    "total_records": 26280,
    "status": "available",
    "last_updated": "2026-07-01T10:00:00Z",
    "sample_data": [
      {
        "datetime": "2023-01-01T00:00:00Z",
        "dry_bulb_temp": 5.20,
        "wet_bulb_temp": 3.10,
        "relative_humidity": 75.00,
        "atmospheric_pressure": 101325,
        "wind_speed": 3.20,
        "solar_radiation": 0
      }
    ]
  }
}
```

### 8.2 从 API 获取气象数据

**POST** `/api/v1/weather/fetch/`

**请求：**
```json
{
  "city_id": 1,
  "years": [2023, 2024, 2025]
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "task_id": "weather-fetch-20260709-001",
    "status": "processing",
    "message": "Fetching weather data for Shanghai (3 years)",
    "estimated_time_seconds": 120
  }
}
```

### 8.3 上传气象数据

**POST** `/api/v1/weather/upload/`

**请求：** 包含 CSV 或 EPW 文件的多部分表单数据

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "records_imported": 26280,
    "years_covered": [2023, 2024, 2025],
    "quality_check": {
      "total_records": 26280,
      "valid_records": 26200,
      "invalid_records": 80,
      "warnings": [
        {
          "row": 1500,
          "field": "dry_bulb_temp",
          "message": "Value out of expected range"
        }
      ]
    }
  }
}
```

---

## 9. 导出 API

### 9.1 导出静态计算报告

**POST** `/api/v1/exports/static-report/{project_id}/`

**请求：**
```json
{
  "format": "pdf",
  "building_ids": null,
  "include_details": true,
  "language": "zh"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "task_id": "export-static-20260709-001",
    "status": "processing",
    "message": "Generating static calculation report",
    "estimated_time_seconds": 30
  }
}
```

### 9.2 导出设备清单

**POST** `/api/v1/exports/equipment-list/{project_id}/`

**请求：**
```json
{
  "format": "excel",
  "building_ids": [1, 2]
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "task_id": "export-equipment-20260709-001",
    "status": "processing"
  }
}
```

### 9.3 下载导出文件

**GET** `/api/v1/exports/download/{task_id}/`

**响应 (200)：** 文件下载（application/pdf、application/vnd.openxmlformats-officedocument.spreadsheetml.sheet、text/csv）

---

## 10. 设置 API

### 10.1 获取水温配置

**GET** `/api/v1/settings/water-temperature/?project={project_id}`

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "project_id": 1,
    "configurations": [
      {
        "id": 1,
        "name": "低温",
        "supply_temp": 7.00,
        "return_temp": 12.00,
        "is_default": true
      },
      {
        "id": 2,
        "name": "中温",
        "supply_temp": 12.00,
        "return_temp": 17.00,
        "is_default": true
      }
    ]
  }
}
```

### 10.2 更新水温配置

**PUT** `/api/v1/settings/water-temperature/{id}/`

**请求：**
```json
{
  "name": "低温（修改）",
  "supply_temp": 6.00,
  "return_temp": 11.00
}
```

### 10.3 获取默认参数

**GET** `/api/v1/settings/defaults/`

**响应 (200)：**
```json
{
  "success": true,
  "data": {
    "system_defaults": {
      "indoor_calc_temp": 26.00,
      "indoor_calc_humidity": 55.00,
      "civil_load_index": 50.00,
      "lighting_load_index": 20.00
    },
    "project_defaults": {
      "project_id": 1,
      "indoor_calc_temp": 25.00,
      "indoor_calc_humidity": 50.00
    }
  }
}
```

---

## 11. WebSocket API

### 11.1 任务进度更新

**连接：** `ws://localhost:8000/ws/tasks/{task_id}/`

**消息（服务端 → 客户端）：**
```json
{
  "type": "progress",
  "data": {
    "task_id": "calc-static-20260709-001",
    "status": "processing",
    "progress": 45,
    "total_items": 135,
    "completed_items": 61,
    "current_item": "Processing room: 电镀车间",
    "message": "Calculating static load for room 61/135"
  }
}
```

```json
{
  "type": "completed",
  "data": {
    "task_id": "calc-static-20260709-001",
    "status": "completed",
    "result_url": "/api/v1/calculations/static/1/",
    "message": "Static calculation completed for 135 rooms"
  }
}
```

```json
{
  "type": "error",
  "data": {
    "task_id": "calc-static-20260709-001",
    "status": "failed",
    "error": {
      "code": "CALCULATION_ERROR",
      "message": "Invalid parameters for room ID 45",
      "room_id": 45
    }
  }
}
```

---

## 12. 对话式采集 API

对话式采集（PRD §6.10）的后端接口，与 Projects/Buildings/Rooms 等 REST 接口共享同一数据模型，采用逐区域提交 / 保存即落库语义。

### 12.1 创建或恢复会话

**POST** `/api/v1/conversation/sessions/`

**请求：**
```json
{ "project_id": 2, "resume_session_id": null }
```

**响应 (200)：**
```json
{ "success": true, "data": { "session_id": "uuid-...", "current_stage": "s1_project", "stage_status": {"s1_project":"done","s2_water_temp":"pending"} } }
```

### 12.2 发送消息（下一问题 + 回答）

**POST** `/api/v1/conversation/sessions/{id}/message/`

**请求：**
```json
{ "message": "3 栋，每栋 5 层" }
```

**响应 (200)：**
```json
{ "success": true, "data": { "stage": "s3_building", "next_question": "请录入第 1 栋的建筑名称", "extracted": {"building_count": 3} } }
```

### 12.3 获取会话状态

**GET** `/api/v1/conversation/sessions/{id}/`

**响应 (200)：** 返回 `current_stage`、`stage_status`、`draft_payload`（断点续采用）。

### 12.4 保存草稿

**PUT** `/api/v1/conversation/sessions/{id}/draft/`

**请求：**
```json
{ "draft_payload": { "rooms": [{"room_name":"光刻间","status":"draft"}] } }
```

**响应 (200)：** `{ "success": true }`（房间以 `room.status = draft` 暂存）。

### 12.5 完成

**POST** `/api/v1/conversation/sessions/{id}/finalize/`

**响应 (200)：** 将草稿 `room.status` 由 draft 转为 active，标记会话完成，返回汇总预览。

## 附录：错误码参考

| 错误码 | HTTP 状态码 | 说明 |
|------|-------------|-------------|
| INVALID_CREDENTIALS | 401 | 用户名或密码无效 |
| TOKEN_EXPIRED | 401 | 访问令牌已过期 |
| INVALID_TOKEN | 401 | 令牌格式无效 |
| INSUFFICIENT_PERMISSIONS | 403 | 用户缺少所需角色 |
| RESOURCE_NOT_FOUND | 404 | 请求的资源不存在 |
| DUPLICATE_RESOURCE | 409 | 资源已存在 |
| VALIDATION_ERROR | 400 | 输入校验失败 |
| CALCULATION_ERROR | 422 | 计算参数无效 |
| WEATHER_DATA_MISSING | 422 | 气象数据不可用 |
| EXPORT_FAILED | 500 | 报表生成失败 |
| INTERNAL_ERROR | 500 | 意外的服务器错误 |
