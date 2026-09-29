#!/bin/bash
# 打包校园消费记账系统为便携版可执行文件

set -e

echo "=========================================="
echo "校园消费记账系统 - 便携版打包脚本"
echo "=========================================="
echo ""

# 进入项目目录
cd "$(dirname "$0")"

echo "步骤 1/5: 构建前端..."
cd frontend
npm run build
cd ..
echo "✓ 前端构建完成"
echo ""

echo "步骤 2/5: 检查依赖..."
pip install -q pyinstaller fastapi uvicorn pydantic pywebview
echo "✓ 依赖检查完成"
echo ""

echo "步骤 3/5: 打包应用..."
pyinstaller --clean portable.spec
echo "✓ 打包完成"
echo ""

echo "步骤 4/5: 创建发布包..."
mkdir -p release
cp dist/校园消费记账系统 release/ 2>/dev/null || true
echo "✓ 发布包创建完成"
echo ""

echo "步骤 5/5: 清理临时文件..."
rm -rf build __pycache__ *.spec.bak
echo "✓ 清理完成"
echo ""

echo "=========================================="
echo "打包成功！"
echo "=========================================="
echo ""
echo "可执行文件位置: dist/校园消费记账系统"
echo "发布包位置: release/校园消费记账系统"
echo ""
echo "运行方式:"
echo "  ./dist/校园消费记账系统"
echo ""
echo "分发方式:"
echo "  将 release/校园消费记账系统 复制到目标电脑即可运行"
echo "  无需安装 Python 或 Node.js"
echo ""
