#!/bin/bash

# 发布脚本 - 用于手动发布poly-query-mcp到PyPI

set -e

echo "🚀 准备发布 poly-query-mcp"

# 检查是否已安装uv
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: uv 未安装，请先安装 uv"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查是否已登录PyPI
echo "📋 检查PyPI认证状态..."
if ! uv publish --dry-run &> /dev/null; then
    echo "❌ 错误: 未配置PyPI认证"
    echo "请设置环境变量: export UV_PUBLISH_TOKEN=pypi-xxxxxxxxxx"
    echo "或运行: uv auth login"
    exit 1
fi

# 清理之前的构建
echo "🧹 清理之前的构建文件..."
rm -rf dist/ build/ *.egg-info/

# 运行测试
echo "🧪 运行测试..."
if [ -d "tests" ]; then
    uv run pytest
else
    echo "⚠️  警告: 未找到测试目录，跳过测试"
fi

# 构建包
echo "📦 构建包..."
uv build

# 检查包
echo "🔍 检查构建的包..."
uv build --check

# 询问发布目标
echo "🎯 选择发布目标:"
echo "1) 测试PyPI (推荐用于测试)"
echo "2) 正式PyPI"
read -p "请输入选择 (1 或 2): " choice

case $choice in
    1)
        echo "📤 发布到测试PyPI..."
        uv publish --publish-url https://test.pypi.org/legacy/
        echo "✅ 已发布到测试PyPI"
        echo "安装命令: uv add --index-url https://test.pypi.org/simple/ poly-query-mcp"
        ;;
    2)
        echo "📤 发布到正式PyPI..."
        uv publish
        echo "✅ 已发布到正式PyPI"
        echo "安装命令: uv add poly-query-mcp"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo "🎉 发布完成！"