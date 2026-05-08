# AI Ops Platform - AI 运维助手

> 轻量级 AI 驱动的服务器运维平台，支持系统监控、Docker 管理、日志查看与 AI 自动告警。

## 功能特性

- 📊 **系统监控** - 实时 CPU / 内存 / 磁盘状态
- 🐳 **Docker 管理** - 容器启停、镜像查看
- 📋 **日志查看** - 支持关键词过滤、尾部追踪
- 🤖 **AI 分析** - 规则引擎自动告警 + 健康报告
- 🚀 **一键部署** - GitHub Actions 自动部署到服务器

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12 + FastAPI |
| 前端 | HTML + TailwindCSS（纯静态）|
| 容器 | Docker + Docker Compose |
| 反代 | Nginx |
| CI/CD | GitHub Actions |
| 部署 | 阿里云 Ubuntu |

## 本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动后端（访问 http://localhost:8000）
uvicorn app.main:app --reload --port 8000

# 3. 打开浏览器
# http://localhost:8000
```

## Docker 部署

```bash
# 构建并启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

访问：`http://your-server:8081`

## API 文档

启动后访问：`http://localhost:8000/docs`

| 接口 | 说明 |
|------|------|
| `GET /api/system/status` | 系统完整状态 |
| `GET /api/docker/containers` | 容器列表 |
| `POST /api/docker/containers/{id}/stop` | 停止容器 |
| `GET /api/logs/read?path=/var/log/syslog&lines=100` | 读日志 |
| `GET /api/ai/analyze` | AI 分析当前状态 |

## 目录结构

```
.
├── app/
│   ├── main.py          # FastAPI 入口
│   └── api/             # API 路由
│       ├── system.py    # 系统状态
│       ├── docker.py    # Docker 管理
│       ├── logs.py      # 日志查看
│       └── ai.py        # AI 分析
├── static/
│   └── index.html       # 前端页面
├── nginx/
│   └── nginx.conf       # Nginx 配置
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .github/workflows/
    └── deploy.yml       # 自动部署
```

## 告警规则

| 指标 | 警告 | 严重 |
|------|------|------|
| CPU | ≥ 80% | ≥ 95% |
| 内存 | ≥ 80% | ≥ 95% |
| 磁盘 | ≥ 85% | ≥ 95% |
