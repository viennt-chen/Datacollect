# 事件数据关联系统 - 使用说明

## 功能概述

事件数据关联系统用于：
1. 根据映射配置筛选过滤有效数据并保存到新的数据库表（event_data除外）
2. 根据event_data中的machine_id、start_time、end_time匹配对应的SV（设定工艺参数）作为PV的限定范围或伺服点位
3. 记录event_data在start_time到end_time期间的报警信息

## 数据库表结构

### 1. event_sv_relations - 事件-SV关联表
存储加工事件与SV(设定工艺参数)的关联关系

### 2. event_pv_relations - 事件-PV关联表
存储加工事件与PV(过程变量)的关联关系，包含对应的SV点位信息

### 3. event_alarm_relations - 事件-报警关联表
存储加工事件期间的报警记录

### 4. event_data_relation_summary - 事件关联汇总表
存储事件的关联统计信息和状态

### 5. point_mapping_configs - 点位映射配置表
定义PV点位与SV点位之间的映射关系

## 数据库迁移

运行迁移脚本创建数据库表：

```bash
cd /home/shxq/code/KP3/WebAdmin
python migrations/create_event_relations.py
```

## API 接口

### 事件关联管理

#### 1. 手动触发事件关联匹配
```
POST /api/event-relations/{event_id}/match
```

#### 2. 获取事件的关联数据
```
GET /api/event-relations/{event_id}
```

返回数据包括：
- summary: 关联统计信息
- sv_data: SV关联数据列表
- pv_data: PV关联数据列表（包含对应的SV点位信息）
- alarm_data: 报警关联数据列表

#### 3. 批量匹配未关联的事件
```
POST /api/event-relations/batch-match?limit=100
```

#### 4. 获取关联统计信息
```
GET /api/event-relations/stats?machine_id=xxx&start_time=xxx&end_time=xxx
```

### 定时任务管理

#### 1. 获取定时任务状态
```
GET /api/event-relations/scheduler/status
```

#### 2. 立即执行一次定时任务
```
POST /api/event-relations/scheduler/run?batch_size=100
```

#### 3. 启动定时任务
```
POST /api/event-relations/scheduler/start?interval=300&batch_size=100
```

#### 4. 停止定时任务
```
POST /api/event-relations/scheduler/stop
```

### 点位映射配置管理

#### 1. 查询点位映射配置列表
```
GET /api/point-mappings/?machine_id=xxx&is_active=true&page=1&page_size=20
```

#### 2. 创建点位映射配置
```
POST /api/point-mappings/
```

请求体示例：
```json
{
  "mapping_name": "压力点位映射",
  "machine_id": "EQ-001",
  "pv_topic": "pv_compress_topic",
  "pv_point_id": "pressure_1",
  "pv_field_name": "pressure",
  "sv_topic": "sv_compress_topic",
  "sv_point_id": "pressure_setpoint",
  "sv_field_name": "set_pressure",
  "mapping_type": "one_to_one",
  "sv_value_range": {"min": 0, "max": 100},
  "is_active": true,
  "description": "压力PV点位到SV设定值的映射"
}
```

#### 3. 更新点位映射配置
```
PUT /api/point-mappings/{mapping_id}
```

#### 4. 删除点位映射配置
```
DELETE /api/point-mappings/{mapping_id}
```

#### 5. 获取设备的点位映射配置
```
GET /api/point-mappings/by-machine/{machine_id}?include_global=true
```

## 自动触发机制

### 实时触发器
当event_data保存时，系统会自动触发关联匹配。触发器在应用启动时自动注册。

### 定时任务
系统会定时批量处理未关联的事件数据。默认每5分钟执行一次，每批处理100个事件。

可以通过环境变量配置：
- `EVENT_RELATION_INTERVAL`: 执行间隔（秒），默认300
- `EVENT_RELATION_BATCH_SIZE`: 批次大小，默认100

## 使用示例

### 1. 配置点位映射

首先需要配置PV点位到SV点位的映射关系：

```bash
curl -X POST http://localhost:8000/api/point-mappings/ \
  -H "Content-Type: application/json" \
  -d '{
    "mapping_name": "温度点位映射",
    "pv_topic": "pv_compress",
    "pv_point_id": "temp_1",
    "sv_topic": "sv_compress",
    "sv_point_id": "temp_setpoint",
    "sv_value_range": {"min": 150, "max": 250},
    "is_active": true
  }'
```

### 2. 手动触发关联匹配

```bash
curl -X POST http://localhost:8000/api/event-relations/123/match
```

### 3. 查询事件关联数据

```bash
curl http://localhost:8000/api/event-relations/123
```

### 4. 批量处理未关联事件

```bash
curl -X POST http://localhost:8000/api/event-relations/batch-match?limit=50
```

### 5. 查看关联统计

```bash
curl http://localhost:8000/api/event-relations/stats
```

## 注意事项

1. 数据库表需要先运行迁移脚本创建
2. 点位映射配置需要在数据匹配前配置好
3. 实时触发器会在event_data保存时自动执行，可能影响写入性能
4. 定时任务默认启用，可以通过API停止
5. SV/PV数据存储在压缩参数表中，需要解压缩后才能使用
