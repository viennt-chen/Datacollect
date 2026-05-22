# WebAdmin - 工业数据管理平台

制造业数据管理系统，支持工艺参数追溯、产品加工信息追溯、生产看板及 WebSocket 实时通信。

## 主要功能

- **工艺参数追溯** - 按设备、产品型号、工艺类型查询和导出工艺参数，支持趋势分析
- **产品加工事件追溯** - 多条件查询产品加工历史，支持统计和 CSV 导出
- **生产看板** - 汇总统计、设备事件计数、报警统计、产出数据
- **MQTT 数据采集** - 订阅 MQTT 主题（ProcesEvent、Alarm、PV、SV），存入 MySQL
- **设备管理** - 设备 CRUD、状态监控、数据源配置（MQTT/数据库）
- **报警管理** - 报警记录、处理流程、按级别/类型统计
- **事件数据关联** - 自动匹配加工事件与 SV/PV 参数及报警记录
- **物料管理** - 物料/产品主数据、物料分类
- **生产工单** - 本地工单管理、ERP（U9）工单定时同步
- **BOM 管理** - 物料清单，支持树形视图、拖拽排序、复制
- **生产流程** - 可视化流程模板、流程实例追踪
- **质量管理** - 质检记录、缺陷类型管理、统计导出
- **WebSocket 实时推送** - 基于主题的发布/订阅实时数据推送
- **用户认证** - JWT 认证、登录锁定、密码策略

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Python 3.12 + FastAPI |
| 数据库 | MySQL + SQLAlchemy |
| 缓存 | Redis（可选） |
| 消息队列 | MQTT (paho-mqtt) |
| 实时通信 | WebSocket |
| 认证 | JWT + bcrypt |
| 序列化 | Protobuf |
| 任务调度 | APScheduler |
| 前端 | Vue.js |

## 快速开始

### 1. 环境配置

复制并编辑环境变量文件：

```bash
cp .env.example .env
```

必需配置：
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
AUTH_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/auth_db
SECRET_KEY=your-secret-key-here
```

可选配置：
```
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
python migrations/create_devices.py
python migrations/create_mqtt_topic_configs.py
# 按需执行其他迁移脚本
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
DEBUG=true python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 访问

- API 文档：http://localhost:8000/docs
- 前端界面：http://localhost:8000/admin

## 项目结构

```
WebAdmin/
├── app/
│   ├── main.py          # 应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── routers/          # API 路由（30+ 模块）
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic 数据模型
│   ├── services/         # 业务逻辑
│   ├── core/             # 认证、缓存、响应处理
│   ├── utils/            # 工具函数
│   └── proto/            # Protobuf 定义
├── migrations/           # 数据库迁移脚本
├── frontend/             # Vue.js 前端
├── proto/                # Protobuf 源文件
├── docs/                 # 文档
├── tests/                # 测试
├── requirements.txt      # Python 依赖
└── Dockerfile            # Docker 配置
```

## API 端点

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `/api/auth` | 登录、登出、Token 刷新 |
| 工艺参数 | `/api/process-params` | 参数查询、导出、趋势 |
| 加工事件 | `/api/processing-events` | 事件查询、统计 |
| 生产看板 | `/api/dashboard` | 汇总数据 |
| 数据采集 | `/api/data-collector` | MQTT 采集控制 |
| 设备管理 | `/api/devices` | 设备 CRUD |
| 报警管理 | `/api/alarms` | 报警记录处理 |
| 物料管理 | `/api/materials` | 物料主数据 |
| 生产工单 | `/api/product-orders` | 工单管理 |
| BOM | `/api/bom` | 物料清单 |
| 质量管理 | `/api/quality-records` | 质检记录 |
| WebSocket | `/ws` | 实时数据推送 |

完整 API 文档请访问 http://localhost:8000/docs

## Docker 部署

```bash
docker build -t webadmin .
docker run -p 8000:8000 --env-file .env webadmin
```

## 许可证

MIT License
