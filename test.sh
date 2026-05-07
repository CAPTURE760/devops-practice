#!/bin/bash
# 简单测试：检查 index.html 是否存在

echo "🔍 开始测试..."

if [ -f "index.html" ]; then
 echo "✅ 测试通过：index.html 存在"
 exit 0
else
 echo "❌ 测试失败：index.html 不存在"
 exit 1
fi
