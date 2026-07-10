# PCB-CoolSim API Design Specification

> Version: 1.0
> Date: 2026-07-09
> Status: Draft
> Base URL: /api/v1

---

## 1. API Overview

### 1.1 Design Principles

- **RESTful:** Resources are nouns, HTTP methods are verbs
- **Versioned:** URL path versioning (`/api/v1/`)
- **Consistent:** Uniform response format across all endpoints
- **Secure:** JWT authentication, role-based authorization
- **Documented:** OpenAPI 3.0 specification

### 1.2 Common Headers

```
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
X-Request-ID: {uuid} (optional, for tracing)
```

### 1.3 Common Response Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Business logic error |
| 500 | Internal Server Error | Server error |

---

## 2. Authentication API

### 2.1 Login

**POST** `/api/v1/auth/login/`

**Request:**
```json
{
  "username": "engineer@example.com",
  "password": "secure_password"
}
```

**Response (200):**
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

**Error (401):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password"
  }
}
```

### 2.2 Refresh Token

**POST** `/api/v1/auth/refresh/`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900
  }
}
```

### 2.3 Logout

**POST** `/api/v1/auth/logout/`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (204):** No Content

---

## 3. Projects API

### 3.1 List Projects

**GET** `/api/v1/projects/`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20, max: 100) |
| search | string | No | Search by name or code |
| status | string | No | Filter by status (active, archived) |

**Response (200):**
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

### 3.2 Create Project

**POST** `/api/v1/projects/`

**Request:**
```json
{
  "project_name": "深圳宝安 PCB 工厂",
  "project_code": "SZ-BA-2026-001",
  "city_id": 2,
  "location": "宝安区XX街道XX号",
  "description": "大型PCB制造工厂"
}
```

**Response (201):**
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

### 3.3 Get Project Details

**GET** `/api/v1/projects/{id}/`

**Response (200):**
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

### 3.4 Update Project

**PUT** `/api/v1/projects/{id}/`

**Request:**
```json
{
  "project_name": "上海松江 AI 服务器 PCB 工厂（二期）",
  "location": "松江区XX路XX号（更新地址）"
}
```

**Response (200):** Same as Get Project Details

### 3.5 Delete Project

**DELETE** `/api/v1/projects/{id}/`

**Response (204):** No Content

### 3.6 Get Project Summary

**GET** `/api/v1/projects/{id}/summary/`

**Response (200):**
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

## 4. Buildings API

### 4.1 List Buildings

**GET** `/api/v1/buildings/?project={project_id}`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project | integer | Yes | Project ID |
| page | integer | No | Page number |
| page_size | integer | No | Items per page |

**Response (200):**
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

### 4.2 Create Building

**POST** `/api/v1/buildings/`

**Request:**
```json
{
  "project_id": 1,
  "building_name": "2#厂房",
  "building_code": "B002",
  "description": "二期生产厂房"
}
```

**Response (201):**
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

## 5. Floors API

### 5.1 List Floors

**GET** `/api/v1/floors/?building={building_id}`

**Response (200):**
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

### 5.2 Create Floor

**POST** `/api/v1/floors/`

**Request:**
```json
{
  "building_id": 1,
  "floor_name": "2F"
}
```

---

## 6. Rooms API

### 6.1 List Rooms

**GET** `/api/v1/rooms/?floor={floor_id}`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| floor | integer | Yes | Floor ID |
| page | integer | No | Page number |
| page_size | integer | No | Items per page |
| search | string | No | Search by name or code |

**Response (200):**
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

### 6.2 Create Room

**POST** `/api/v1/rooms/`

**Request:**
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

**Response (201):**
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

### 6.3 Get Room Details

**GET** `/api/v1/rooms/{id}/`

**Response (200):**
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

### 6.4 Update Room

**PUT** `/api/v1/rooms/{id}/`

**Request:** Same as Create Room (partial updates supported)

### 6.5 Delete Room

**DELETE** `/api/v1/rooms/{id}/`

**Response (204):** No Content

---

## 7. Calculations API

### 7.1 Calculate Static Load (Single Room)

**POST** `/api/v1/rooms/{id}/calculate-static/`

**Request:** No body required (uses current room parameters)

**Response (200):**
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

### 7.2 Calculate Static Load (Batch)

**POST** `/api/v1/projects/{id}/calculate-static/`

**Request:**
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

### 7.3 Get Static Calculation Results

**GET** `/api/v1/calculations/static/{project_id}/`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| building_id | integer | No | Filter by building |
| floor_id | integer | No | Filter by floor |
| water_tier_id | integer | No | Filter by water temperature tier |

**Response (200):**
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

### 7.4 Run Dynamic Simulation

**POST** `/api/v1/projects/{id}/simulate/`

**Request:**
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

### 7.5 Get Simulation Results

**GET** `/api/v1/calculations/dynamic/{project_id}/`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| room_id | integer | No | Filter by room |
| year | integer | No | Filter by year |
| month | integer | No | Filter by month |
| aggregation | string | No | hourly, daily, monthly |

**Response (200):**
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

## 8. Weather API

### 8.1 Get Weather Data

**GET** `/api/v1/weather/?city={city_id}`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| city | integer | Yes | City ID |
| year | integer | No | Filter by year |
| start_date | string | No | Start date (YYYY-MM-DD) |
| end_date | string | No | End date (YYYY-MM-DD) |

**Response (200):**
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

### 8.2 Fetch Weather Data from API

**POST** `/api/v1/weather/fetch/`

**Request:**
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

### 8.3 Upload Weather Data

**POST** `/api/v1/weather/upload/`

**Request:** Multipart form data with CSV or EPW file

**Response (200):**
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

## 9. Exports API

### 9.1 Export Static Calculation Report

**POST** `/api/v1/exports/static-report/{project_id}/`

**Request:**
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

### 9.2 Export Equipment List

**POST** `/api/v1/exports/equipment-list/{project_id}/`

**Request:**
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

### 9.3 Download Exported File

**GET** `/api/v1/exports/download/{task_id}/`

**Response (200):** File download (application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv)

---

## 10. Settings API

### 10.1 Get Water Temperature Configurations

**GET** `/api/v1/settings/water-temperature/?project={project_id}`

**Response (200):**
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

### 10.2 Update Water Temperature Configuration

**PUT** `/api/v1/settings/water-temperature/{id}/`

**Request:**
```json
{
  "name": "低温（修改）",
  "supply_temp": 6.00,
  "return_temp": 11.00
}
```

### 10.3 Get Default Parameters

**GET** `/api/v1/settings/defaults/`

**Response (200):**
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

### 11.1 Task Progress Updates

**Connection:** `ws://localhost:8000/ws/tasks/{task_id}/`

**Messages (Server → Client):**
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

## Appendix: Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_CREDENTIALS | 401 | Invalid username or password |
| TOKEN_EXPIRED | 401 | Access token expired |
| INVALID_TOKEN | 401 | Invalid token format |
| INSUFFICIENT_PERMISSIONS | 403 | User lacks required role |
| RESOURCE_NOT_FOUND | 404 | Requested resource doesn't exist |
| DUPLICATE_RESOURCE | 409 | Resource already exists |
| VALIDATION_ERROR | 400 | Input validation failed |
| CALCULATION_ERROR | 422 | Calculation parameters invalid |
| WEATHER_DATA_MISSING | 422 | Weather data not available |
| EXPORT_FAILED | 500 | Report generation failed |
| INTERNAL_ERROR | 500 | Unexpected server error |
