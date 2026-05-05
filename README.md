# LifeHub - 全方位个人生活管理系统

LifeHub 是一个融合了 [Mulanbay（木兰湾）](https://github.com/mulanbay/mulanbay-server3) 和 [Personal Management System (PMS)](https://github.com/Volmarg/personal-management-system) 设计理念的全方位个人生活管理系统。支持 Docker 一键部署，覆盖消费、锻炼、阅读、健康、饮食、人生经历等全场景管理。

## 功能模块

| 模块 | 功能说明 |
|------|---------|
| 仪表盘 | 全局数据概览，收支趋势图表，关键指标展示 |
| 财务管理 | 收入/支出记录，分类管理，预算设置，财务统计 |
| 健康管理 | 体重、血压、心率、血糖、体脂率等指标记录 |
| 运动记录 | 跑步、骑行、游泳等 10+ 运动类型，时长/距离/卡路里追踪 |
| 饮食管理 | 三餐 + 加餐记录，食物库管理，热量统计 |
| 待办事项 | 优先级管理，状态追踪，到期提醒 |
| 笔记管理 | 笔记创建/编辑，分类管理，置顶/归档 |
| 习惯追踪 | 每日/每周/每月习惯打卡，目标设定 |
| 阅读管理 | 书架管理，阅读进度追踪，书评评分 |
| 人生经历 | 旅行/成就/里程碑等人生重要事件时间线 |
| 联系人 | 通讯录管理，分组管理 |
| 密码管理 | 安全密码存储，一键显示/隐藏 |
| 目标管理 | 目标设定，进度追踪，完成率可视化 |
| 个人设置 | 个人信息修改，密码修改 |

## 技术栈

### 后端
- **Python 3.12** + **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy 2.0** - 异步 ORM
- **PostgreSQL 16** - 主数据库
- **Redis 7** - 缓存
- **Pydantic v2** - 数据验证

### 前端
- **Vue 3** + **Composition API**
- **Element Plus** - UI 组件库
- **ECharts** - 数据可视化
- **Pinia** - 状态管理
- **Vue Router 4** - 路由
- **Vite 6** - 构建工具

### 部署
- **Docker Compose** - 一键部署
- **Nginx** - 反向代理 + 静态资源服务

## 快速部署

### 前置要求
- Docker >= 20.10
- Docker Compose >= 2.0

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd lifehub

# 启动所有服务
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f
```

启动完成后，访问 **http://localhost** 即可使用系统。

### 默认信息
- **访问地址**: http://localhost
- **API 文档**: http://localhost/api/docs (通过 nginx 代理)
- **数据库**: PostgreSQL @ localhost:5432
  - 数据库名: `lifehub`
  - 用户名: `lifehub`
  - 密码: `lifehub123`

### 首次使用
1. 访问 http://localhost
2. 点击「注册」创建账号
3. 登录后即可开始使用

## 常用命令

```bash
# 构建（不使用缓存）
make build

# 启动服务
make up

# 停止服务
make down

# 重启服务
make restart

# 查看日志
make logs

# 查看后端日志
make backend-logs

# 清理所有数据（危险操作）
make clean
```

## 项目结构

```
lifehub/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── api/            # API 调用
│   │   ├── components/     # 组件
│   │   ├── layouts/        # 布局
│   │   ├── router/         # 路由
│   │   ├── stores/         # 状态管理
│   │   ├── styles/         # 样式
│   │   └── views/          # 页面
│   ├── Dockerfile
│   └── nginx.conf
├── docker/                  # Docker 配置
│   └── postgres/
│       └── init.sql        # 数据库初始化
├── docker-compose.yml       # Docker Compose 配置
├── Makefile                 # 便捷命令
└── README.md
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `postgresql+asyncpg://lifehub:lifehub123@postgres:5432/lifehub` | 数据库连接 |
| `REDIS_URL` | `redis://redis:6379/0` | Redis 连接 |
| `SECRET_KEY` | `lifehub-secret-key-...` | JWT 密钥（生产环境请修改） |

## 致谢

本项目的设计灵感来源于以下优秀的开源项目：

- [Mulanbay（木兰湾）](https://github.com/mulanbay/mulanbay-server3) - 全方位生活管理系统
- [Personal Management System (PMS)](https://github.com/Volmarg/personal-management-system) - 个人数据管理中心

## License

MIT
