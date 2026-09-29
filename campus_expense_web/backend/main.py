"""
校园消费记账系统 - FastAPI后端服务
将原有PyQt5业务逻辑重构为REST API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
import sqlite3
import os
import sys

app = FastAPI(title="校园消费记账API", version="2.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据模型
class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="金额，必须大于0")
    category: str = Field(..., min_length=1, description="分类名称")
    description: str = Field(default="", description="描述")
    date: str = Field(..., description="日期，格式YYYY-MM-DD")


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str
    date: str
    created_at: str


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20, description="分类名称")
    icon: str = Field(default="📌", description="图标")


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    is_default: bool


class BudgetUpdate(BaseModel):
    amount: float = Field(..., gt=0, description="月度预算金额")


class BudgetResponse(BaseModel):
    monthly_budget: Optional[float]
    spent: float
    remaining: float
    percentage: float


# 数据库类（复用原有逻辑）
class Database:
    def __init__(self, db_name="campus_expenses.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS expenses
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      amount REAL NOT NULL,
                      category TEXT NOT NULL,
                      description TEXT,
                      date TEXT NOT NULL,
                      created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

        c.execute('''CREATE TABLE IF NOT EXISTS categories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE NOT NULL,
                      icon TEXT DEFAULT '📌',
                      is_default INTEGER DEFAULT 0)''')

        c.execute('''CREATE TABLE IF NOT EXISTS budget
                     (id INTEGER PRIMARY KEY,
                      monthly_budget REAL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS settings
                     (key TEXT PRIMARY KEY,
                      value TEXT)''')

        # 插入默认分类
        default_categories = [
            ("餐饮", "🍜"), ("交通", "🚌"), ("学习", "📚"), ("娱乐", "🎮"),
            ("社交", "👥"), ("购物", "🛒"), ("医疗", "💊"), ("其他", "📌")
        ]
        for name, icon in default_categories:
            try:
                c.execute("INSERT INTO categories (name, icon, is_default) VALUES (?, ?, 1)",
                          (name, icon))
            except sqlite3.IntegrityError:
                pass

        self.conn.commit()

    def add_expense(self, amount, category, description, date_str):
        c = self.conn.cursor()
        c.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                  (amount, category, description, date_str))
        self.conn.commit()
        return c.lastrowid

    def get_expenses(self, year=None, month=None):
        c = self.conn.cursor()
        if year and month:
            c.execute("""SELECT * FROM expenses 
                        WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                        ORDER BY date DESC, id DESC""",
                      (str(year), f"{month:02d}"))
        else:
            c.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
        return [dict(row) for row in c.fetchall()]

    def delete_expense(self, expense_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return c.rowcount > 0

    def get_monthly_total(self, year, month):
        c = self.conn.cursor()
        c.execute("""SELECT COALESCE(SUM(amount), 0) FROM expenses
                    WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?""",
                  (str(year), f"{month:02d}"))
        return c.fetchone()[0]

    def get_category_stats(self, year, month):
        c = self.conn.cursor()
        c.execute("""SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                    GROUP BY category ORDER BY total DESC""",
                  (str(year), f"{month:02d}"))
        return [dict(row) for row in c.fetchall()]

    def get_categories(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY id")
        return [dict(row) for row in c.fetchall()]

    def add_category(self, name, icon="📌"):
        c = self.conn.cursor()
        c.execute("INSERT INTO categories (name, icon, is_default) VALUES (?, ?, 0)",
                  (name, icon))
        self.conn.commit()
        return c.lastrowid

    def delete_category(self, category_id):
        c = self.conn.cursor()
        c.execute("SELECT is_default FROM categories WHERE id = ?", (category_id,))
        row = c.fetchone()
        if row and row['is_default']:
            return False
        c.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()
        return c.rowcount > 0

    def set_budget(self, amount):
        c = self.conn.cursor()
        c.execute("DELETE FROM budget")
        c.execute("INSERT INTO budget (monthly_budget) VALUES (?)", (amount,))
        self.conn.commit()

    def get_budget(self):
        c = self.conn.cursor()
        c.execute("SELECT monthly_budget FROM budget LIMIT 1")
        row = c.fetchone()
        return row['monthly_budget'] if row else None

    def export_csv(self, filepath):
        import csv
        c = self.conn.cursor()
        c.execute("SELECT id, date, category, description, amount FROM expenses ORDER BY date")
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', '日期', '分类', '描述', '金额'])
            writer.writerows(c.fetchall())


# 全局数据库实例
if getattr(sys, 'frozen', False):
    _base = os.path.dirname(sys.executable)
else:
    _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(_base, "campus_expenses.db")
db = Database(db_path)


# API路由
@app.get("/")
async def root():
    return {"message": "校园消费记账API v2.0"}


@app.get("/api/expenses", response_model=List[ExpenseResponse])
async def get_expenses(year: Optional[int] = None, month: Optional[int] = None):
    """获取消费记录，支持按月筛选"""
    expenses = db.get_expenses(year, month)
    return expenses


@app.post("/api/expenses", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate):
    """添加消费记录"""
    try:
        datetime.strptime(expense.date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")

    expense_id = db.add_expense(expense.amount, expense.category, expense.description, expense.date)
    return {
        "id": expense_id,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "date": expense.date,
        "created_at": datetime.now().isoformat()
    }


@app.delete("/api/expenses/{expense_id}")
async def delete_expense(expense_id: int):
    """删除消费记录"""
    if not db.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}


@app.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories():
    """获取所有分类"""
    categories = db.get_categories()
    return [{"id": c['id'], "name": c['name'], "icon": c['icon'], "is_default": bool(c['is_default'])}
            for c in categories]


@app.post("/api/categories", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    """添加自定义分类"""
    try:
        cat_id = db.add_category(category.name, category.icon)
        return {"id": cat_id, "name": category.name, "icon": category.icon, "is_default": False}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="分类名称已存在")


@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: int):
    """删除自定义分类"""
    if not db.delete_category(category_id):
        raise HTTPException(status_code=400, detail="无法删除默认分类或分类不存在")
    return {"message": "删除成功"}


@app.get("/api/budget", response_model=BudgetResponse)
async def get_budget():
    """获取预算信息"""
    budget = db.get_budget()
    today = date.today()
    spent = db.get_monthly_total(today.year, today.month)

    if budget is None:
        return {
            "monthly_budget": None,
            "spent": spent,
            "remaining": 0,
            "percentage": 0
        }

    remaining = budget - spent
    percentage = (spent / budget * 100) if budget > 0 else 0

    return {
        "monthly_budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percentage": percentage
    }


@app.put("/api/budget")
async def set_budget(budget: BudgetUpdate):
    """设置月度预算"""
    db.set_budget(budget.amount)
    return {"message": f"预算已设置为 ¥{budget.amount:.2f}"}


@app.get("/api/statistics/{year}/{month}")
async def get_statistics(year: int, month: int):
    """获取月度统计"""
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="月份必须在1-12之间")

    total = db.get_monthly_total(year, month)
    categories = db.get_category_stats(year, month)

    return {
        "year": year,
        "month": month,
        "total": total,
        "categories": categories
    }


@app.get("/api/export")
async def export_csv():
    """导出CSV"""
    import tempfile
    from fastapi.responses import FileResponse

    filepath = os.path.join(tempfile.gettempdir(), "campus_expenses_export.csv")
    db.export_csv(filepath)

    return FileResponse(
        filepath,
        media_type="text/csv",
        filename="campus_expenses.csv",
        headers={"Content-Disposition": "attachment; filename=campus_expenses.csv"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
