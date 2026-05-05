# Superpower Life OS

基于 superpower 的工程规范（本地优先、隐私优先、模块清晰、可 Docker 部署），融合
[Mulanbay](https://github.com/mulanbay/mulanbay-server3) 的全方位生活记录理念与
[Personal Management System](https://github.com/Volmarg/personal-management-system)
的一站式个人数据中心思路，构建的个人全方位生活管理系统。

它不是对两个开源项目的复制粘贴，而是一个可本地运行的轻量实现：单容器、SQLite 持久化、
标准库后端和原生前端，适合个人 NAS、家用服务器或本机 Docker 部署。这里的
“superpower 编码规范”落实为：小而清晰的模块、无隐藏外部依赖、可读的数据边界、默认本地
隐私保护和一条命令部署。

## 功能范围

| 来源灵感 | 本系统模块 | 说明 |
| --- | --- | --- |
| Mulanbay | 消费、锻炼、阅读、健康、饮食、人生经历 | 覆盖日常行为记录、生活评分、趋势预测 |
| PMS | 待办、笔记、密码、联系人、账单 | 覆盖个人数据中心常用模块 |
| Mulanbay AI/ML | 快速自然语言录入、洞察、滚动预测 | 完全离线 deterministic parser，不上传隐私数据 |
| Mulanbay 提醒 | 本地提醒中心 | 支持按日期和渠道保存提醒 |
| PMS 本地数据 | SQLite + JSON 导出 | 数据目录挂载在 `./data` |

## 快速开始

```bash
docker compose up --build
```

打开：

```text
http://localhost:8000
```

首次启动会写入一组演示数据，数据库保存在：

```text
./data/life_os.sqlite3
```

## 配置

`docker-compose.yml` 中可以调整：

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `APP_PORT` | `8000` | 服务监听端口 |
| `DATA_DIR` | `/app/data` | 容器内数据目录 |
| `DATABASE_PATH` | `/app/data/life_os.sqlite3` | SQLite 文件位置 |
| `PASSWORD_SECRET` | `change-me-in-compose` | 本地密码库混淆密钥 |
| `TZ` | `Asia/Shanghai` | 容器时区 |

> 密码模块使用本地密钥进行轻量混淆，适合个人离线部署。若要用于高敏感密码管理，请迁移到
> 专业密钥管理方案或增加主密码派生加密。

## API 概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/health` | 健康检查 |
| `GET` | `/api/modules` | 模块元数据 |
| `GET` | `/api/dashboard` | 仪表盘、评分、洞察和到期提醒 |
| `GET` | `/api/records?module=expense` | 查询记录 |
| `POST` | `/api/records` | 新增结构化记录 |
| `PUT` | `/api/records/{id}` | 更新记录 |
| `DELETE` | `/api/records/{id}` | 删除记录 |
| `POST` | `/api/quick-entry` | 自然语言快速录入 |
| `GET` | `/api/reminders` | 查询提醒 |
| `POST` | `/api/reminders` | 新增提醒 |
| `PUT` | `/api/reminders/{id}` | 标记提醒完成 |
| `GET` | `/api/forecast` | 本地滚动趋势预测 |
| `GET` | `/api/export` | 导出记录与提醒 |

自然语言录入示例：

```json
{"text": "昨天跑步 35 分钟 5 公里 #运动"}
```

```json
{"text": "午餐花了 38 元 #餐饮"}
```

## 本地开发

```bash
python -m app.server
```

运行测试：

```bash
python -m unittest
```

## 设计原则

- **本地优先**：应用、数据库、分析都在本机或自有服务器运行。
- **隐私优先**：快速录入和预测不依赖外部 AI 服务。
- **单一部署单元**：一个 Docker Compose 命令即可启动。
- **模块可演进**：各生活模块统一使用 `records` 表承载，差异字段放入 `details`。
- **可迁移**：提供 JSON 导出接口，SQLite 文件可直接备份。

