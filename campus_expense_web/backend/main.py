"""
校园消费记账系统 - FastAPI后端服务
将原有PyQt5业务逻辑重构为REST API
"""

import csv
import io
import math
import os
import re
import sqlite3
import sys
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, field_validator

# SQLite 的 strftime 只认严格补零的 ISO 日期，'2026-9-5' 会返回 NULL 从而
# 被月度统计静默丢弃（记录列表能看到、统计和饼图里却没有），因此入库前必须挡住
DATE_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()


app = FastAPI(title="校园消费记账API", version="3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _make_json_safe(value: Any) -> Any:
    # 请求体里的 NaN/Infinity 会被 Python 的 json 解析成 float，原样回显到错误详情时
    # JSONResponse 会因 allow_nan=False 抛 ValueError，本该 422 的响应就变成了 500
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: _make_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_make_json_safe(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": _make_json_safe(jsonable_encoder(exc.errors()))},
    )


class ExpenseCreate(BaseModel):
    # allow_inf_nan=False 是必须的：Python 的 json 会接受 Infinity/NaN 字面量，
    # 而 gt=0 对 +inf 成立，一旦写进 SQLite，之后所有读接口都会因为
    # JSONResponse 的 allow_nan=False 序列化失败而永久返回 500
    amount: float = Field(..., gt=0, allow_inf_nan=False, description="金额，必须大于0")
    category: str = Field(..., min_length=1, description="分类名称")
    description: str = Field(default="", max_length=200, description="描述")
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

    @field_validator("name", "icon", mode="before")
    @classmethod
    def strip_whitespace(cls, v: Any) -> Any:
        # 先去空白再校验长度：否则 "   " 能绕过 min_length=1 建出空分类，
        # "餐饮 " 也会被当成与 "餐饮" 不同的分类，导致统计里同一类裂成两条
        return v.strip() if isinstance(v, str) else v


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    is_default: bool


class BudgetUpdate(BaseModel):
    amount: float = Field(..., gt=0, allow_inf_nan=False, description="月度预算金额")


class BudgetResponse(BaseModel):
    monthly_budget: Optional[float]
    spent: float
    remaining: float
    percentage: float


class RestorePayload(BaseModel):
    """恢复备份的请求体。字段放宽松（备份可能来自不同版本），
    逐条记录的合法性在路由里校验后才写入。"""

    version: Optional[str] = None
    expenses: List[Dict[str, Any]] = Field(default_factory=list)
    categories: List[Dict[str, Any]] = Field(default_factory=list)
    budget: Optional[float] = None


class Database:
    def __init__(self, db_name="campus_expenses.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS expenses
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      amount REAL NOT NULL,
                      category TEXT NOT NULL,
                      description TEXT,
                      date TEXT NOT NULL,
                      created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS categories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE NOT NULL,
                      icon TEXT DEFAULT '📌',
                      is_default INTEGER DEFAULT 0)"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS budget
                     (id INTEGER PRIMARY KEY,
                      monthly_budget REAL)"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS settings
                     (key TEXT PRIMARY KEY,
                      value TEXT)"""
        )

        default_categories = [
            ("餐饮", "🍜"),
            ("交通", "🚌"),
            ("学习", "📚"),
            ("娱乐", "🎮"),
            ("社交", "👥"),
            ("购物", "🛒"),
            ("医疗", "💊"),
            ("其他", "📌"),
        ]
        for name, icon in default_categories:
            try:
                c.execute(
                    "INSERT INTO categories (name, icon, is_default) VALUES (?, ?, 1)", (name, icon)
                )
            except sqlite3.IntegrityError:
                pass

        self.conn.commit()

    def add_expense(self, amount, category, description, date_str):
        c = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT INTO expenses (amount, category, description, date, created_at) VALUES (?, ?, ?, ?, ?)",
            (amount, category, description, date_str, now),
        )
        self.conn.commit()
        return c.lastrowid, now

    def get_expenses(
        self,
        year=None,
        month=None,
        keyword=None,
        category=None,
        date_from=None,
        date_to=None,
        min_amount=None,
        max_amount=None,
    ):
        c = self.conn.cursor()
        # 原先要求 year 和 month 必须同时给出，否则静默返回全量，
        # 调用方只传 year 时会以为筛选生效了
        conditions = []
        params = []
        if year is not None:
            conditions.append("strftime('%Y', date) = ?")
            params.append(str(year))
        if month is not None:
            conditions.append("strftime('%m', date) = ?")
            params.append(f"{month:02d}")
        if keyword:
            # 描述或分类里任一处命中即算匹配
            conditions.append("(description LIKE ? OR category LIKE ?)")
            like = f"%{keyword}%"
            params.extend([like, like])
        if category:
            conditions.append("category = ?")
            params.append(category)
        if date_from:
            conditions.append("date >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("date <= ?")
            params.append(date_to)
        if min_amount is not None:
            conditions.append("amount >= ?")
            params.append(min_amount)
        if max_amount is not None:
            conditions.append("amount <= ?")
            params.append(max_amount)
        where = f"WHERE {' AND '.join(conditions)} " if conditions else ""
        c.execute(f"SELECT * FROM expenses {where}ORDER BY date DESC, id DESC", params)
        return [dict(row) for row in c.fetchall()]

    def get_expense(self, expense_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        row = c.fetchone()
        return dict(row) if row else None

    def update_expense(self, expense_id, amount, category, description, date_str):
        c = self.conn.cursor()
        c.execute(
            "UPDATE expenses SET amount = ?, category = ?, description = ?, date = ? WHERE id = ?",
            (amount, category, description, date_str, expense_id),
        )
        self.conn.commit()
        return c.rowcount > 0

    def delete_expense(self, expense_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return c.rowcount > 0

    def get_monthly_total(self, year, month):
        c = self.conn.cursor()
        c.execute(
            """SELECT COALESCE(SUM(amount), 0) FROM expenses
                    WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?""",
            (str(year), f"{month:02d}"),
        )
        return c.fetchone()[0]

    def get_category_stats(self, year, month):
        c = self.conn.cursor()
        c.execute(
            """SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                    GROUP BY category ORDER BY total DESC""",
            (str(year), f"{month:02d}"),
        )
        return [dict(row) for row in c.fetchall()]

    def get_categories(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY id")
        return [dict(row) for row in c.fetchall()]

    def add_category(self, name, icon="📌"):
        c = self.conn.cursor()
        c.execute("INSERT INTO categories (name, icon, is_default) VALUES (?, ?, 0)", (name, icon))
        self.conn.commit()
        return c.lastrowid

    def delete_category(self, category_id):
        c = self.conn.cursor()
        c.execute("SELECT is_default FROM categories WHERE id = ?", (category_id,))
        row = c.fetchone()
        if row and row["is_default"]:
            return False
        c.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()
        return c.rowcount > 0

    def set_budget(self, amount):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO budget (id, monthly_budget) VALUES (1, ?)", (amount,))
        self.conn.commit()

    def get_budget(self):
        c = self.conn.cursor()
        c.execute("SELECT monthly_budget FROM budget LIMIT 1")
        row = c.fetchone()
        return row["monthly_budget"] if row else None

    def replace_all(self, expenses, categories, budget):
        """整库替换（恢复备份）：单事务，失败回滚，原有数据不受损。

        只替换自定义分类，不动内置默认分类——这样即使恢复一份不含默认分类的
        备份，也不会把内置的 8 个分类弄丢。
        """
        c = self.conn.cursor()
        try:
            c.execute("DELETE FROM expenses")
            c.execute("DELETE FROM sqlite_sequence WHERE name = 'expenses'")
            c.execute("DELETE FROM categories WHERE is_default = 0")
            c.execute("DELETE FROM budget")

            for e in expenses:
                c.execute(
                    "INSERT INTO expenses (id, amount, category, description, date, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        e.get("id"),
                        e["amount"],
                        e["category"],
                        e.get("description") or "",
                        e["date"],
                        e.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
            for cat in categories or []:
                if cat.get("is_default"):
                    continue
                c.execute(
                    "INSERT OR IGNORE INTO categories (name, icon, is_default) VALUES (?, ?, 0)",
                    (cat["name"], cat.get("icon", "📌")),
                )
            if budget is not None:
                c.execute(
                    "INSERT OR REPLACE INTO budget (id, monthly_budget) VALUES (1, ?)", (budget,)
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()

    def build_csv(self):
        c = self.conn.cursor()
        c.execute("SELECT id, date, category, description, amount FROM expenses ORDER BY date")
        buf = io.StringIO(newline="")
        writer = csv.writer(buf)
        writer.writerow(["ID", "日期", "分类", "描述", "金额"])
        writer.writerows(c.fetchall())
        # utf-8-sig 带 BOM，Excel 直接打开中文才不乱码
        return buf.getvalue().encode("utf-8-sig")


def _get_db_path() -> str:
    env_path = os.environ.get("DB_PATH")
    if env_path:
        return env_path
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "campus_expenses.db")
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "campus_expenses.db"
    )


db = Database(_get_db_path())


@app.get("/")
async def root():
    return {"message": "校园消费记账API v3.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "3.0"}


@app.get("/api/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    year: Optional[int] = None,
    month: Optional[int] = None,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
):
    if month is not None and not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="月份必须在1-12之间")
    expenses = db.get_expenses(
        year, month, keyword, category, date_from, date_to, min_amount, max_amount
    )
    return expenses


@app.post("/api/expenses", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate):
    if not DATE_PATTERN.match(expense.date):
        raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")
    try:
        parsed = datetime.strptime(expense.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期不存在")

    expense_id, created_at = db.add_expense(
        expense.amount, expense.category, expense.description, parsed.isoformat()
    )
    return {
        "id": expense_id,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "date": parsed.isoformat(),
        "created_at": created_at,
    }


@app.delete("/api/expenses/{expense_id}")
async def delete_expense(expense_id: int):
    if not db.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}


@app.put("/api/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: int, expense: ExpenseCreate):
    if not DATE_PATTERN.match(expense.date):
        raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")
    try:
        parsed = datetime.strptime(expense.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期不存在")

    if not db.update_expense(
        expense_id, expense.amount, expense.category, expense.description, parsed.isoformat()
    ):
        raise HTTPException(status_code=404, detail="记录不存在")

    return db.get_expense(expense_id)


@app.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories():
    categories = db.get_categories()
    return [
        {"id": c["id"], "name": c["name"], "icon": c["icon"], "is_default": bool(c["is_default"])}
        for c in categories
    ]


@app.post("/api/categories", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    try:
        cat_id = db.add_category(category.name, category.icon)
        return {"id": cat_id, "name": category.name, "icon": category.icon, "is_default": False}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="分类名称已存在")


@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: int):
    if not db.delete_category(category_id):
        raise HTTPException(status_code=400, detail="无法删除默认分类或分类不存在")
    return {"message": "删除成功"}


@app.get("/api/budget", response_model=BudgetResponse)
async def get_budget():
    budget = db.get_budget()
    today = date.today()
    spent = db.get_monthly_total(today.year, today.month)

    if budget is None:
        return {"monthly_budget": None, "spent": spent, "remaining": 0, "percentage": 0}

    remaining = budget - spent
    percentage = (spent / budget * 100) if budget > 0 else 0

    return {
        "monthly_budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percentage": percentage,
    }


@app.put("/api/budget")
async def set_budget(budget: BudgetUpdate):
    db.set_budget(budget.amount)
    return {"message": f"预算已设置为 ¥{budget.amount:.2f}"}


@app.get("/api/statistics/{year}/{month}")
async def get_statistics(year: int, month: int):
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="月份必须在1-12之间")

    total = db.get_monthly_total(year, month)
    categories = db.get_category_stats(year, month)

    return {"year": year, "month": month, "total": total, "categories": categories}


@app.get("/api/export")
async def export_csv():
    # 不再落临时文件：固定可预测的 /tmp 路径能被同机其他用户用符号链接劫持，
    # 让服务进程覆写任意文件，而且导出后的残留文件从不清理
    filename = f"campus_expenses_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=db.build_csv(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/api/backup")
async def backup_data():
    # 全量 JSON 备份：单机应用的"保命"接口，含记录 / 分类 / 预算
    return {
        "version": "3.0",
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expenses": db.get_expenses(),
        "categories": db.get_categories(),
        "budget": db.get_budget(),
    }


@app.post("/api/restore")
async def restore_data(payload: RestorePayload):
    # 写入前逐条校验：坏备份宁可整包拒绝，也不要写进半个库
    for e in payload.expenses:
        amount = e.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
            raise HTTPException(status_code=400, detail="备份格式错误：记录金额非法")
        if not isinstance(e.get("category"), str) or not e["category"]:
            raise HTTPException(status_code=400, detail="备份格式错误：记录缺少分类")
        if not isinstance(e.get("date"), str) or not DATE_PATTERN.match(e["date"]):
            raise HTTPException(status_code=400, detail=f"备份中有非法日期：{e.get('date')}")

    db.replace_all(payload.expenses, payload.categories, payload.budget)
    return {"message": f"恢复成功：{len(payload.expenses)} 条记录"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
