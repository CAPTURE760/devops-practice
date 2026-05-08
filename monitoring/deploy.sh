#!/bin/bash
# 监控栈一键部署脚本
# 用法：./deploy-monitoring.sh

set -e

MONITOR_DIR="/home/deploy/monitoring"

echo "========== 监控栈部署开始 =========="

# 1. 创建监控目录
sudo mkdir -p $MONITOR_DIR
cd $MONITOR_DIR

# 2. 把本地 monitoring 目录同步到服务器（这里是从 Git clone 下来的代码里复制）
# 如果 monitoring 目录在 /home/deploy/devops-practice 里，就复制过来
if [ -d /home/deploy/devops-practice/monitoring ]; then
    sudo cp -r /home/deploy/devops-practice/monitoring/* $MONITOR_DIR/
    echo "✅ 监控配置已复制"
else
    echo "⚠️ 未找到 monitoring 目录，跳过配置同步"
fi

# 3. 安装 docker-compose（如果没有）
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装 docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ docker-compose 安装完成"
else
    echo "✅ docker-compose 已存在"
fi

# 4. 拉取监控镜像
echo "📦 拉取监控镜像（首次需要几分钟）..."
cd $MONITOR_DIR
sudo docker-compose -f docker-compose.monitoring.yml pull

# 5. 停止旧容器（如果存在）
echo "🛑 停止旧监控容器..."
sudo docker-compose -f docker-compose.monitoring.yml down || true

# 6. 启动监控栈
echo "🚀 启动监控栈..."
sudo docker-compose -f docker-compose.monitoring.yml up -d

# 7. 等待启动
echo "⏳ 等待服务启动..."
sleep 10

# 8. 健康检查
echo "✅ 验证各服务状态..."
sudo docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(prometheus|grafana|cadvisor|node-exporter)"

echo ""
echo "========== 监控栈部署完成 =========="
echo "Prometheus: http://121.196.170.9:9090"
echo "Grafana:    http://121.196.170.9:3030  (admin / admin123)"
echo "cAdvisor:   http://121.196.170.9:9080"
echo "Node Exp:   http://121.196.170.9:9100"
