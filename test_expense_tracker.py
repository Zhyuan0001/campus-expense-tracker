"""
校园消费记账 GUI - 单元测试
覆盖：数据库操作、输入校验、统计计算、边界情况
"""

import os
import sys
import csv
import tempfile
import sqlite3
import pytest
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campus_expense_tracker import Database, DEFAULT_CATEGORIES


@pytest.fixture
def db():
    """创建临时数据库"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = Database(path)
    yield database
    database.close()
    os.unlink(path)


class TestDatabaseInit:
    """数据库初始化测试"""

    def test_default_categories_created(self, db):
        cats = db.get_all_categories()
        assert len(cats) == 8
        names = [c["name"] for c in cats]
        for default_cat in DEFAULT_CATEGORIES:
            assert default_cat in names

    def test_categories_ordered_by_id(self, db):
        cats = db.get_all_categories()
        names = [c["name"] for c in cats]
        assert names == DEFAULT_CATEGORIES

    def test_all_default_categories_marked(self, db):
        cats = db.get_all_categories()
        for cat in cats:
            assert cat["is_default"] == 1

    def test_no_expenses_on_init(self, db):
        assert len(db.get_all_expenses()) == 0

    def test_no_budget_on_init(self, db):
        assert db.get_budget() is None


class TestExpenseOperations:
    """消费记录操作测试"""

    def test_add_expense(self, db):
        db.add_expense(15.5, "餐饮", "午饭", "2026-09-29")
        expenses = db.get_all_expenses()
        assert len(expenses) == 1
        assert expenses[0]["amount"] == 15.5
        assert expenses[0]["category"] == "餐饮"
        assert expenses[0]["description"] == "午饭"
        assert expenses[0]["date"] == "2026-09-29"

    def test_add_multiple_expenses(self, db):
        db.add_expense(10.0, "餐饮", "早餐", "2026-09-28")
        db.add_expense(20.0, "交通", "打车", "2026-09-29")
        db.add_expense(50.0, "购物", "买书", "2026-09-29")
        assert len(db.get_all_expenses()) == 3

    def test_add_expense_without_description(self, db):
        db.add_expense(10.0, "餐饮", "", "2026-09-29")
        expenses = db.get_all_expenses()
        assert expenses[0]["description"] == ""

    def test_delete_expense(self, db):
        db.add_expense(15.5, "餐饮", "午饭", "2026-09-29")
        expense_id = db.get_all_expenses()[0]["id"]
        db.delete_expense(expense_id)
        assert len(db.get_all_expenses()) == 0

    def test_delete_nonexistent_expense(self, db):
        db.delete_expense(9999)
        assert len(db.get_all_expenses()) == 0

    def test_expenses_ordered_by_date_desc(self, db):
        db.add_expense(10.0, "餐饮", "Day1", "2026-09-01")
        db.add_expense(20.0, "交通", "Day2", "2026-09-15")
        db.add_expense(30.0, "学习", "Day3", "2026-09-10")
        expenses = db.get_all_expenses()
        dates = [e["date"] for e in expenses]
        assert dates == sorted(dates, reverse=True)


class TestMonthlyQuery:
    """月度查询测试"""

    def test_filter_by_month(self, db):
        db.add_expense(10.0, "餐饮", "Sep", "2026-09-15")
        db.add_expense(20.0, "交通", "Oct", "2026-10-10")
        db.add_expense(30.0, "学习", "Sep", "2026-09-20")

        sep = db.get_expenses_by_month(2026, 9)
        assert len(sep) == 2

        oct = db.get_expenses_by_month(2026, 10)
        assert len(oct) == 1

    def test_empty_month(self, db):
        db.add_expense(10.0, "餐饮", "Sep", "2026-09-15")
        result = db.get_expenses_by_month(2026, 3)
        assert len(result) == 0

    def test_monthly_total(self, db):
        db.add_expense(15.5, "餐饮", "A", "2026-09-01")
        db.add_expense(20.0, "交通", "B", "2026-09-15")
        db.add_expense(100.0, "购物", "C", "2026-10-01")

        total_sep = db.get_monthly_total(2026, 9)
        assert total_sep == pytest.approx(35.5)

        total_oct = db.get_monthly_total(2026, 10)
        assert total_oct == pytest.approx(100.0)

    def test_monthly_total_empty(self, db):
        total = db.get_monthly_total(2026, 1)
        assert total == 0.0


class TestCategoryStatistics:
    """分类统计测试"""

    def test_category_totals(self, db):
        db.add_expense(15.0, "餐饮", "A", "2026-09-01")
        db.add_expense(25.0, "餐饮", "B", "2026-09-05")
        db.add_expense(10.0, "交通", "C", "2026-09-10")

        totals = db.get_category_totals(2026, 9)
        assert len(totals) == 2

        cat_map = {row["category"]: row["total"] for row in totals}
        assert cat_map["餐饮"] == pytest.approx(40.0)
        assert cat_map["交通"] == pytest.approx(10.0)

    def test_category_totals_sorted_by_amount_desc(self, db):
        db.add_expense(10.0, "交通", "A", "2026-09-01")
        db.add_expense(50.0, "餐饮", "B", "2026-09-02")
        db.add_expense(30.0, "购物", "C", "2026-09-03")

        totals = db.get_category_totals(2026, 9)
        amounts = [row["total"] for row in totals]
        assert amounts == sorted(amounts, reverse=True)

    def test_category_totals_empty(self, db):
        totals = db.get_category_totals(2026, 9)
        assert len(totals) == 0

    def test_percentages_sum_to_100(self, db):
        db.add_expense(15.0, "餐饮", "A", "2026-09-01")
        db.add_expense(25.0, "交通", "B", "2026-09-05")
        db.add_expense(10.0, "学习", "C", "2026-09-10")

        total = db.get_monthly_total(2026, 9)
        totals = db.get_category_totals(2026, 9)
        pct_sum = sum((row["total"] / total * 100) for row in totals)
        assert pct_sum == pytest.approx(100.0, abs=0.1)


class TestCustomCategories:
    """自定义分类测试"""

    def test_add_category(self, db):
        db.add_category("宠物")
        cats = db.get_all_categories()
        names = [c["name"] for c in cats]
        assert "宠物" in names

    def test_add_duplicate_category_raises(self, db):
        with pytest.raises(sqlite3.IntegrityError):
            db.add_category("餐饮")

    def test_delete_custom_category(self, db):
        db.add_category("宠物")
        cats = db.get_all_categories()
        pet_id = [c["id"] for c in cats if c["name"] == "宠物"][0]
        db.delete_category(pet_id)
        names = [c["name"] for c in db.get_all_categories()]
        assert "宠物" not in names

    def test_cannot_delete_default_category(self, db):
        cats = db.get_all_categories()
        default_id = [c["id"] for c in cats if c["name"] == "餐饮"][0]
        db.delete_category(default_id)
        names = [c["name"] for c in db.get_all_categories()]
        assert "餐饮" in names

    def test_category_names_for_combo(self, db):
        names = db.get_active_category_names()
        assert len(names) == 8
        assert "餐饮" in names


class TestBudget:
    """预算测试"""

    def test_set_and_get_budget(self, db):
        db.set_budget(2000.0)
        assert db.get_budget() == pytest.approx(2000.0)

    def test_update_budget(self, db):
        db.set_budget(2000.0)
        db.set_budget(3000.0)
        assert db.get_budget() == pytest.approx(3000.0)

    def test_budget_not_set(self, db):
        assert db.get_budget() is None


class TestSettings:
    """设置测试"""

    def test_set_and_get_setting(self, db):
        db.set_setting("theme", "dark")
        assert db.get_setting("theme") == "dark"

    def test_get_default_setting(self, db):
        assert db.get_setting("theme", "light") == "light"

    def test_update_setting(self, db):
        db.set_setting("theme", "dark")
        db.set_setting("theme", "light")
        assert db.get_setting("theme") == "light"


class TestCSVExport:
    """CSV 导出测试"""

    def test_export_format(self, db):
        db.add_expense(15.5, "餐饮", "午饭", "2026-09-29")
        db.add_expense(30.0, "交通", "打车", "2026-09-28")

        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            rows = db.get_all_expenses()
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "日期", "分类", "描述", "金额"])
                for row in rows:
                    writer.writerow([row["id"], row["date"], row["category"],
                                     row["description"] or "", f"{row['amount']:.2f}"])

            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader)
                assert header == ["ID", "日期", "分类", "描述", "金额"]
                data_rows = list(reader)
                assert len(data_rows) == 2
        finally:
            os.unlink(path)


class TestInputValidation:
    """输入校验逻辑测试（验证应用层应实现的校验规则）"""

    def test_amount_must_be_positive(self):
        assert 15.5 > 0
        assert not (0 > 0)
        assert not (-5 > 0)

    def test_amount_string_is_invalid(self):
        with pytest.raises(ValueError):
            float("abc")

    def test_date_format_validation(self):
        valid = datetime.strptime("2026-09-29", "%Y-%m-%d")
        assert valid.year == 2026

        with pytest.raises(ValueError):
            datetime.strptime("2026-13-01", "%Y-%m-%d")

        with pytest.raises(ValueError):
            datetime.strptime("hello", "%Y-%m-%d")

    def test_empty_category_name_invalid(self):
        name = ""
        assert not name.strip()

    def test_duplicate_category_name(self, db):
        existing = [c["name"] for c in db.get_all_categories()]
        assert "餐饮" in existing
