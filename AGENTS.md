# AGENTS.md - 校园消费记账系统

## 项目概述
大学生生活费记账桌面 GUI 应用。支持记录消费、分类统计（含饼图可视化）、月度分析、预算提醒、自定义分类、数据导出 CSV、亮/暗主题切换。

## 技术栈
- Python 3.10+
- PyQt5（GUI 框架）
- SQLite3（数据存储，Python 内置）
- matplotlib（图表，嵌入 PyQt5）
- pytest（测试框架）

## 构建与运行命令
```bash
# 安装依赖
pip install PyQt5 matplotlib

# 运行主程序
python campus_expense_tracker.py

# 运行测试
pytest test_expense_tracker.py -v
```

## 代码风格规范
- 遵循 PEP8
- 类名 PascalCase，函数/变量 snake_case
- 中文界面，中文注释
- 单文件主程序（约 810 行）

## 项目结构
```
SofteareEnjineer/
├── campus_expense_tracker.py   # 主程序（单文件）
├── test_expense_tracker.py     # 单元测试
├── DESIGN.md                   # 设计文档
├── AGENTS.md                   # 本文件
├── iteration_log.md            # 迭代记录
└── campus_expenses.db          # SQLite 数据库（运行时生成）
```

## 数据库结构
- **expenses**: id, amount, category, description, date, created_at
- **categories**: id, name, icon, is_default
- **budget**: id, monthly_budget
- **settings**: key, value（存储主题等配置）

## 不变量（严禁修改）
- 数据库表名和字段名
- 默认 8 种分类：餐饮、交通、学习、娱乐、社交、购物、医疗、其他
- CSV 导出列顺序：ID,日期,分类,描述,金额
- 文件命名约定

## 测试说明
- 使用 pytest 运行 test_expense_tracker.py
- 测试覆盖：输入校验、数据库操作、统计计算、边界情况
- 测试使用临时数据库文件，不污染生产数据

## 安全注意事项
- 金额输入必须为正数
- 日期格式严格校验
- 删除操作需二次确认
- 分类名不可重复、不可为空
