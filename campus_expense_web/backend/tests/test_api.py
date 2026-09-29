"""
FastAPI 后端 API 测试
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import os
import tempfile
import time
import uuid


@pytest.fixture
def client():
    """创建测试客户端，使用临时数据库"""
    # 创建临时数据库文件
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # 设置环境变量使用临时数据库
    os.environ['TEST_DB_PATH'] = temp_db.name
    
    with TestClient(app) as c:
        yield c
    
    # 清理临时数据库
    if os.path.exists(temp_db.name):
        try:
            os.unlink(temp_db.name)
        except:
            pass
    if 'TEST_DB_PATH' in os.environ:
        del os.environ['TEST_DB_PATH']


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
