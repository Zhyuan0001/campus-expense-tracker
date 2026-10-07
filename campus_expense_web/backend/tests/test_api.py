"""
FastAPI 后端 API 测试
"""
import pytest
from fastapi.testclient import TestClient
import main
import os
import tempfile
import uuid


@pytest.fixture
def client():
    """创建测试客户端，使用临时数据库"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    original_db = main.db
    main.db = main.Database(temp_db.name)

    with TestClient(main.app) as c:
        yield c

    main.db.close()
    main.db = original_db

    if os.path.exists(temp_db.name):
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


class TestExpensesAPI:
    """消费记录 API 测试"""
    
    def test_create_expense(self, client):
        """测试创建消费记录"""
        response = client.post("/api/expenses", json={
            "amount": 25.5,
            "category": "餐饮",
            "description": "午餐",
            "date": "2026-09-29"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 25.5
        assert data["category"] == "餐饮"
        assert "id" in data
    
    def test_create_expense_invalid_amount(self, client):
        """测试创建消费记录 - 无效金额"""
        response = client.post("/api/expenses", json={
            "amount": -10,
            "category": "餐饮",
            "description": "测试",
            "date": "2026-09-29"
        })
        assert response.status_code == 422
    
    def test_create_expense_zero_amount(self, client):
        """测试创建消费记录 - 零金额"""
        response = client.post("/api/expenses", json={
            "amount": 0,
            "category": "餐饮",
            "description": "测试",
            "date": "2026-09-29"
        })
        assert response.status_code == 422
    
    def test_get_expenses(self, client):
        """测试获取消费记录列表"""
        # 先创建一条记录
        client.post("/api/expenses", json={
            "amount": 30,
            "category": "交通",
            "description": "地铁",
            "date": "2026-09-29"
        })
        
        # 获取记录列表
        response = client.get("/api/expenses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_expenses_with_filter(self, client):
        """测试获取消费记录列表 - 带筛选条件"""
        # 创建两条不同月份的记录
        client.post("/api/expenses", json={
            "amount": 30,
            "category": "交通",
            "description": "9月地铁",
            "date": "2026-09-15"
        })
        client.post("/api/expenses", json={
            "amount": 50,
            "category": "餐饮",
            "description": "10月午餐",
            "date": "2026-10-15"
        })
        
        # 筛选9月记录
        response = client.get("/api/expenses?year=2026&month=9")
        assert response.status_code == 200
        data = response.json()
        assert all(exp["date"].startswith("2026-09") for exp in data)
    
    def test_delete_expense(self, client):
        """测试删除消费记录"""
        # 创建记录
        create_response = client.post("/api/expenses", json={
            "amount": 20,
            "category": "学习",
            "description": "书籍",
            "date": "2026-09-29"
        })
        expense_id = create_response.json()["id"]
        
        # 删除记录
        delete_response = client.delete(f"/api/expenses/{expense_id}")
        assert delete_response.status_code == 200
        
        # 验证已删除
        get_response = client.get("/api/expenses")
        expenses = get_response.json()
        assert not any(exp["id"] == expense_id for exp in expenses)
    
    def test_delete_nonexistent_expense(self, client):
        """测试删除不存在的消费记录"""
        response = client.delete("/api/expenses/99999")
        assert response.status_code == 404


class TestCategoriesAPI:
    """分类管理 API 测试"""
    
    def test_get_categories(self, client):
        """测试获取所有分类"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 应该有默认分类
        assert len(data) >= 8
    
    def test_create_category(self, client):
        """测试创建自定义分类"""
        unique_name = f"测试分类_{uuid.uuid4().hex[:8]}"
        response = client.post("/api/categories", json={
            "name": unique_name,
            "icon": "🧪"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == unique_name
        assert data["icon"] == "🧪"
        assert "id" in data
    
    def test_create_duplicate_category(self, client):
        """测试创建重复分类"""
        unique_name = f"重复分类_{uuid.uuid4().hex[:8]}"
        # 第一次创建
        client.post("/api/categories", json={
            "name": unique_name,
            "icon": "📌"
        })
        
        # 第二次创建同名分类
        response = client.post("/api/categories", json={
            "name": unique_name,
            "icon": "📌"
        })
        assert response.status_code == 400
    
    def test_create_empty_category_name(self, client):
        """测试创建空名称分类"""
        response = client.post("/api/categories", json={
            "name": "",
            "icon": "📌"
        })
        assert response.status_code == 422
    
    def test_delete_custom_category(self, client):
        """测试删除自定义分类"""
        unique_name = f"待删除分类_{uuid.uuid4().hex[:8]}"
        # 创建自定义分类
        create_response = client.post("/api/categories", json={
            "name": unique_name,
            "icon": "🗑️"
        })
        category_id = create_response.json()["id"]
        
        # 删除分类
        delete_response = client.delete(f"/api/categories/{category_id}")
        assert delete_response.status_code == 200
    
    def test_delete_default_category(self, client):
        """测试删除默认分类（应该失败）"""
        # 获取默认分类
        categories = client.get("/api/categories").json()
        default_category = next((c for c in categories if c["is_default"]), None)
        
        if default_category:
            response = client.delete(f"/api/categories/{default_category['id']}")
            assert response.status_code == 400


class TestStatisticsAPI:
    """统计数据 API 测试"""
    
    def test_get_monthly_statistics(self, client):
        """测试获取月度统计"""
        # 创建一些记录
        client.post("/api/expenses", json={
            "amount": 100,
            "category": "餐饮",
            "description": "测试",
            "date": "2026-09-15"
        })
        client.post("/api/expenses", json={
            "amount": 50,
            "category": "交通",
            "description": "测试",
            "date": "2026-09-20"
        })
        
        response = client.get("/api/statistics/2026/9")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "categories" in data
        assert data["total"] >= 150
    
    def test_get_monthly_statistics_invalid_month(self, client):
        """测试获取月度统计 - 无效月份"""
        response = client.get("/api/statistics/2026/13")
        assert response.status_code == 400
    
    def test_get_category_statistics(self, client):
        """测试获取分类统计（通过月度统计接口）"""
        # 创建记录
        client.post("/api/expenses", json={
            "amount": 80,
            "category": "餐饮",
            "description": "测试",
            "date": "2026-09-15"
        })
        
        response = client.get("/api/statistics/2026/9")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data


class TestBudgetAPI:
    """预算管理 API 测试"""
    
    def test_set_budget(self, client):
        """测试设置预算"""
        response = client.put("/api/budget", json={
            "amount": 1000
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_get_budget(self, client):
        """测试获取预算"""
        # 先设置预算
        client.put("/api/budget", json={"amount": 1500})
        
        response = client.get("/api/budget")
        assert response.status_code == 200
        data = response.json()
        assert "monthly_budget" in data


class TestExportAPI:
    """数据导出 API 测试"""
    
    def test_export_csv(self, client):
        """测试导出 CSV"""
        # 创建一些记录
        client.post("/api/expenses", json={
            "amount": 100,
            "category": "餐饮",
            "description": "测试导出",
            "date": "2026-09-15"
        })
        
        response = client.get("/api/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


# 注意：主题设置API尚未实现，这些测试暂时注释掉
# 如果需要实现，请在main.py中添加相应的端点

# class TestSettingsAPI:
#     """设置 API 测试"""
#     
#     def test_set_theme(self, client):
#         """测试设置主题"""
#         response = client.post("/api/settings/theme", json={
#             "theme": "dark"
#         })
#         assert response.status_code == 200
#     
#     def test_get_theme(self, client):
#         """测试获取主题"""
#         # 先设置主题
#         client.post("/api/settings/theme", json={"theme": "light"})
#         
#         response = client.get("/api/settings/theme")
#         assert response.status_code == 200
#         data = response.json()
#         assert "theme" in data


class TestDefectRegressions:
    """黑盒测试发现的缺陷回归用例

    这些场景原先 19 个测试全部通过却一个都没覆盖到：TestClient 走 ASGI 内存调用，
    且用例从不发送 Infinity/NaN、非补零日期、纯空白分类名，也不校验 CSV 字节内容。
    """

    def test_infinity_amount_rejected_and_not_persisted(self, client):
        """D1: Infinity 曾被写入数据库，此后所有读接口永久 500"""
        response = client.post("/api/expenses", json={
            "amount": float("inf"),
            "category": "餐饮",
            "description": "",
            "date": "2026-09-15"
        })
        assert response.status_code == 422

        # 关键是脏数据没有落库，读接口必须仍然可用
        assert client.get("/api/expenses").status_code == 200
        assert client.get("/api/budget").status_code == 200
        assert client.get("/api/statistics/2026/9").status_code == 200

    def test_nan_amount_returns_422_not_500(self, client):
        """D2: NaN 曾让错误详情无法 JSON 序列化，返回 500"""
        response = client.post("/api/expenses", json={
            "amount": float("nan"),
            "category": "餐饮",
            "description": "",
            "date": "2026-09-15"
        })
        assert response.status_code == 422
        assert response.json()["detail"]

    def test_infinity_budget_rejected(self, client):
        """D3: 预算 Infinity 曾被接受，导致 GET /api/budget 永久 500"""
        assert client.put("/api/budget", json={"amount": float("inf")}).status_code == 422
        assert client.get("/api/budget").status_code == 200

    def test_non_padded_date_rejected(self, client):
        """D4: '2026-9-5' 曾被接受，但 SQLite strftime 认不出，统计里被静默丢弃"""
        response = client.post("/api/expenses", json={
            "amount": 22,
            "category": "餐饮",
            "description": "",
            "date": "2026-9-5"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "日期格式错误，应为YYYY-MM-DD"

    def test_calendar_impossible_date_rejected(self, client):
        """2026-02-30 能通过格式正则但不是合法日期"""
        response = client.post("/api/expenses", json={
            "amount": 10,
            "category": "餐饮",
            "description": "",
            "date": "2026-02-30"
        })
        assert response.status_code == 400

    def test_statistics_total_equals_record_sum(self, client):
        """D4 的实际后果：记录列表合计必须等于统计总额，否则账不平"""
        for day in ("2026-09-05", "2026-09-20"):
            client.post("/api/expenses", json={
                "amount": 11,
                "category": "餐饮",
                "description": "",
                "date": day
            })
        records = client.get("/api/expenses", params={"year": 2026, "month": 9}).json()
        stats = client.get("/api/statistics/2026/9").json()
        assert len(records) == 2
        assert stats["total"] == pytest.approx(sum(r["amount"] for r in records))

    def test_whitespace_category_name_rejected(self, client):
        """D5: '   ' 曾绕过 min_length=1 建出空分类"""
        assert client.post("/api/categories", json={"name": "   "}).status_code == 422

    def test_category_name_is_trimmed(self, client):
        """D5: '餐饮 ' 曾与 '餐饮' 并存，同一分类在统计里裂成两条"""
        response = client.post("/api/categories", json={"name": "宠物 "})
        assert response.status_code == 200
        assert response.json()["name"] == "宠物"
        # 去空白后与刚建的分类重名，必须被拒绝
        assert client.post("/api/categories", json={"name": " 宠物"}).status_code == 400

    def test_export_csv_bytes(self, client):
        """D6: 导出改为内存生成，不再写可预测的临时文件（符号链接劫持风险）"""
        client.post("/api/expenses", json={
            "amount": 100,
            "category": "餐饮",
            "description": '含,逗号和"引号"',
            "date": "2026-09-15"
        })
        response = client.get("/api/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

        expected_header = "\ufeffID,日期,分类,描述,金额\r\n".encode("utf-8")
        assert response.content.startswith(expected_header)
        assert '"含,逗号和""引号"""'.encode("utf-8") in response.content

    def test_year_only_filter_is_applied(self, client):
        """D8: 只传 year 时筛选曾被静默忽略，返回全量"""
        for day in ("2025-09-15", "2026-09-15"):
            client.post("/api/expenses", json={
                "amount": 1,
                "category": "餐饮",
                "description": "",
                "date": day
            })
        data = client.get("/api/expenses", params={"year": 2026}).json()
        assert len(data) == 1
        assert data[0]["date"] == "2026-09-15"

    def test_month_only_filter_is_applied(self, client):
        """D8: 只传 month 同样要生效"""
        for day in ("2026-08-15", "2026-09-15"):
            client.post("/api/expenses", json={
                "amount": 1,
                "category": "餐饮",
                "description": "",
                "date": day
            })
        data = client.get("/api/expenses", params={"month": 9}).json()
        assert len(data) == 1
        assert data[0]["date"] == "2026-09-15"


class TestExpenseUpdateAPI:
    """编辑记录 API 测试（PUT /api/expenses/{id}）"""

    def _create(self, client, **kw):
        payload = {"amount": 20, "category": "餐饮", "description": "原描述", "date": "2026-09-15"}
        payload.update(kw)
        return client.post("/api/expenses", json=payload).json()["id"]

    def test_update_expense(self, client):
        eid = self._create(client)
        response = client.put(f"/api/expenses/{eid}", json={
            "amount": 99.5,
            "category": "交通",
            "description": "改成地铁",
            "date": "2026-09-20"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == eid
        assert data["amount"] == 99.5
        assert data["category"] == "交通"
        assert data["description"] == "改成地铁"
        assert data["date"] == "2026-09-20"

    def test_update_persists(self, client):
        eid = self._create(client)
        client.put(f"/api/expenses/{eid}", json={
            "amount": 5, "category": "学习", "description": "", "date": "2026-09-16"
        })
        rows = client.get("/api/expenses").json()
        row = next(x for x in rows if x["id"] == eid)
        assert row["amount"] == 5
        assert row["category"] == "学习"

    def test_update_nonexistent_expense(self, client):
        response = client.put("/api/expenses/99999", json={
            "amount": 1, "category": "餐饮", "description": "", "date": "2026-09-15"
        })
        assert response.status_code == 404

    def test_update_with_invalid_date(self, client):
        eid = self._create(client)
        response = client.put(f"/api/expenses/{eid}", json={
            "amount": 1, "category": "餐饮", "description": "", "date": "2026-9-5"
        })
        assert response.status_code == 400

    def test_update_with_invalid_amount_does_not_touch_row(self, client):
        eid = self._create(client)
        assert client.put(f"/api/expenses/{eid}", json={
            "amount": -5, "category": "餐饮", "description": "", "date": "2026-09-15"
        }).status_code == 422
        rows = client.get("/api/expenses").json()
        assert next(x for x in rows if x["id"] == eid)["amount"] == 20


class TestSearchFilterAPI:
    """搜索 / 筛选 API 测试"""

    def _seed(self, client):
        client.post("/api/expenses", json={
            "amount": 10, "category": "餐饮", "description": "食堂午饭", "date": "2026-09-10"})
        client.post("/api/expenses", json={
            "amount": 50, "category": "交通", "description": "地铁月卡", "date": "2026-09-20"})
        client.post("/api/expenses", json={
            "amount": 200, "category": "购物", "description": "买鞋", "date": "2026-10-05"})

    def test_keyword_matches_description(self, client):
        self._seed(client)
        data = client.get("/api/expenses", params={"keyword": "地铁"}).json()
        assert len(data) == 1
        assert data[0]["category"] == "交通"

    def test_keyword_matches_category(self, client):
        self._seed(client)
        data = client.get("/api/expenses", params={"keyword": "购物"}).json()
        assert len(data) == 1
        assert data[0]["description"] == "买鞋"

    def test_filter_by_category(self, client):
        self._seed(client)
        data = client.get("/api/expenses", params={"category": "餐饮"}).json()
        assert len(data) == 1
        assert data[0]["description"] == "食堂午饭"

    def test_filter_by_date_range(self, client):
        self._seed(client)
        data = client.get("/api/expenses", params={
            "date_from": "2026-09-15", "date_to": "2026-09-30"}).json()
        assert len(data) == 1
        assert data[0]["category"] == "交通"

    def test_filter_by_amount_range(self, client):
        self._seed(client)
        data = client.get("/api/expenses", params={"min_amount": 40, "max_amount": 100}).json()
        assert len(data) == 1
        assert data[0]["amount"] == 50

    def test_combined_filters(self, client):
        self._seed(client)
        data = client.get("/api/expenses", params={"keyword": "地铁", "min_amount": 100}).json()
        assert data == []


class TestBackupRestoreAPI:
    """备份 / 恢复 API 测试"""

    def test_backup_structure(self, client):
        client.post("/api/expenses", json={
            "amount": 12, "category": "餐饮", "description": "x", "date": "2026-09-15"})
        client.put("/api/budget", json={"amount": 800})
        response = client.get("/api/backup")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "3.0"
        assert len(data["expenses"]) == 1
        assert len(data["categories"]) >= 8
        assert data["budget"] == 800

    def test_restore_replaces_all_data(self, client):
        client.post("/api/expenses", json={
            "amount": 12, "category": "餐饮", "description": "旧", "date": "2026-09-15"})
        response = client.post("/api/restore", json={
            "version": "3.0",
            "expenses": [
                {"amount": 30, "category": "交通", "description": "新记录1", "date": "2026-10-01"},
                {"amount": 40, "category": "学习", "description": "新记录2", "date": "2026-10-02"},
            ],
            "categories": [],
            "budget": 1500,
        })
        assert response.status_code == 200
        rows = client.get("/api/expenses").json()
        assert len(rows) == 2
        assert all("新记录" in x["description"] for x in rows)
        assert client.get("/api/budget").json()["monthly_budget"] == 1500

    def test_restore_rejects_bad_amount(self, client):
        response = client.post("/api/restore", json={
            "expenses": [
                {"amount": -1, "category": "餐饮", "description": "", "date": "2026-09-15"}],
        })
        assert response.status_code == 400

    def test_restore_rejects_bad_date(self, client):
        response = client.post("/api/restore", json={
            "expenses": [
                {"amount": 1, "category": "餐饮", "description": "", "date": "2026-9-5"}],
        })
        assert response.status_code == 400

    def test_restore_keeps_default_categories(self, client):
        """恢复一份不含默认分类的备份，内置的 8 个分类不能被清掉"""
        response = client.post("/api/restore", json={"expenses": [], "categories": []})
        assert response.status_code == 200
        categories = client.get("/api/categories").json()
        assert len([c for c in categories if c["is_default"]]) >= 8

    def test_backup_restore_roundtrip(self, client):
        for i in range(3):
            client.post("/api/expenses", json={
                "amount": 10 + i, "category": "餐饮", "description": f"r{i}", "date": "2026-09-15"})
        backup = client.get("/api/backup").json()

        client.post("/api/restore", json={"expenses": [], "categories": []})
        assert client.get("/api/expenses").json() == []

        client.post("/api/restore", json=backup)
        rows = client.get("/api/expenses").json()
        assert len(rows) == 3
        assert sorted(r["description"] for r in rows) == ["r0", "r1", "r2"]
