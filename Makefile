.PHONY: help install install-backend install-frontend test test-backend test-frontend lint lint-backend lint-frontend format format-backend format-frontend clean run run-dev

help:
	@echo "校园消费记账系统 - 开发命令"
	@echo ""
	@echo "安装依赖:"
	@echo "  make install          - 安装所有依赖"
	@echo "  make install-backend  - 安装后端依赖"
	@echo "  make install-frontend - 安装前端依赖"
	@echo ""
	@echo "运行应用:"
	@echo "  make run              - 生产模式运行"
	@echo "  make run-dev          - 开发模式运行（热重载）"
	@echo ""
	@echo "测试:"
	@echo "  make test             - 运行所有测试"
	@echo "  make test-backend     - 运行后端测试"
	@echo "  make test-frontend    - 运行前端测试"
	@echo ""
	@echo "代码质量:"
	@echo "  make lint             - 检查代码质量"
	@echo "  make lint-backend     - 检查后端代码"
	@echo "  make lint-frontend    - 检查前端代码"
	@echo "  make format           - 格式化代码"
	@echo "  make format-backend   - 格式化后端代码"
	@echo "  make format-frontend  - 格式化前端代码"
	@echo ""
	@echo "其他:"
	@echo "  make clean            - 清理临时文件"

# 安装依赖
install: install-backend install-frontend

install-backend:
	@echo "安装后端依赖..."
	cd campus_expense_web/backend && pip install -r requirements.txt
	cd campus_expense_web/backend && pip install -r requirements-dev.txt

install-frontend:
	@echo "安装前端依赖..."
	cd campus_expense_web/frontend && npm install

# 运行应用
run:
	@echo "生产模式运行..."
	cd campus_expense_web/frontend && npm run build
	cd campus_expense_web && python3 app.py

run-dev:
	@echo "开发模式运行..."
	cd campus_expense_web && DEV_MODE=1 python3 app.py

# 测试
test: test-backend test-frontend

test-backend:
	@echo "运行后端测试..."
	cd campus_expense_web/backend && python3 -m pytest tests/ -v

test-frontend:
	@echo "运行前端测试..."
	cd campus_expense_web/frontend && npm run test:run

# 代码质量检查
lint: lint-backend lint-frontend

lint-backend:
	@echo "检查后端代码..."
	cd campus_expense_web/backend && black --check main.py
	cd campus_expense_web/backend && isort --check-only main.py
	cd campus_expense_web/backend && flake8 main.py --max-line-length=100 --ignore=E501,W503

lint-frontend:
	@echo "检查前端代码..."
	cd campus_expense_web/frontend && npx prettier --check "src/**/*.{vue,ts,js}"
	cd campus_expense_web/frontend && npm run lint || true

# 代码格式化
format: format-backend format-frontend

format-backend:
	@echo "格式化后端代码..."
	cd campus_expense_web/backend && black main.py
	cd campus_expense_web/backend && isort main.py

format-frontend:
	@echo "格式化前端代码..."
	cd campus_expense_web/frontend && npx prettier --write "src/**/*.{vue,ts,js}"

# 清理
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.db" -delete 2>/dev/null || true
