#!/bin/bash
# 自动部署脚本 - GitHub Actions 调用
# 路径: /home/deploy/devops-practice

set -e  # 任何命令失败则停止

echo "===== 开始自动部署 ====="
echo "时间: $(date)"

# 进入项目目录
cd /home/deploy/devops-practice

# 拉取最新代码
echo ">>> 拉取 Git 最新代码..."
git pull origin main

# 构建 Docker 镜像
echo ">>> 构建 Docker 镜像..."
sudo docker build -t devops-app:latest .

# 停止旧容器（如果存在）
echo ">>> 停止旧容器..."
sudo docker stop devops-app 2>/dev/null || true
sudo docker rm devops-app 2>/dev/null || true

# 启动新容器
echo ">>> 启动新容器..."
sudo docker run -d \
  --name devops-app \
  -p 8081:80 \
  --restart unless-stopped \
  devops-app:latest

# 验证
echo ">>> 验证容器运行状态..."
sudo docker ps | grep devops-app

echo "===== 部署完成 ====="