"""
校园消费记账 GUI
技术栈：Python 3.10 + PyQt5 + SQLite3 + matplotlib
功能：记账、查看记录、分类统计(饼图)、预算提醒、自定义分类、CSV导出、主题切换
"""

import sys
import os
import csv
import sqlite3
from datetime import datetime, date

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox,
    QFileDialog, QDoubleSpinBox, QGroupBox, QFormLayout, QSplitter,
    QAbstractItemView, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

_cjk_font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_cjk_font_path):
    fm.fontManager.addfont(_cjk_font_path)
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP"] + plt.rcParams["font.sans-serif"]
else:
    for _f in ["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"]:
        plt.rcParams["font.sans-serif"] = [_f] + plt.rcParams["font.sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus_expenses.db")
DEFAULT_CATEGORIES = ["餐饮", "交通", "学习", "娱乐", "社交", "购物", "医疗", "其他"]

LIGHT_STYLE = """
QMainWindow { background-color: #f5f6fa; }
QTabWidget::pane { border: 1px solid #dcdde1; border-radius: 6px; background: white; }
QTabBar::tab { background: #dfe6e9; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; font-size: 13px; }
QTabBar::tab:selected { background: #0984e3; color: white; font-weight: bold; }
QPushButton { background-color: #0984e3; color: white; border: none; padding: 8px 20px; border-radius: 4px; font-size: 13px; }
QPushButton:hover { background-color: #74b9ff; }
QPushButton#danger { background-color: #d63031; }
QPushButton#danger:hover { background-color: #e17055; }
QPushButton#success { background-color: #00b894; }
QPushButton#success:hover { background-color: #55efc4; }
QTableWidget { gridline-color: #dfe6e9; border: 1px solid #dcdde1; border-radius: 4px; font-size: 13px; }
QTableWidget::item:selected { background-color: #74b9ff; color: white; }
QHeaderView::section { background-color: #0984e3; color: white; padding: 6px; border: none; font-weight: bold; }
QGroupBox { font-weight: bold; border: 1px solid #dcdde1; border-radius: 6px; margin-top: 10px; padding-top: 15px; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox { padding: 6px; border: 1px solid #b2bec3; border-radius: 4px; font-size: 13px; background: white; }
QLabel#title { font-size: 18px; font-weight: bold; color: #2d3436; padding: 8px; }
QLabel#total { font-size: 20px; font-weight: bold; color: #d63031; }
QLabel#status_green { color: #00b894; font-size: 14px; font-weight: bold; }
QLabel#status_yellow { color: #fdcb6e; font-size: 14px; font-weight: bold; }
QLabel#status_red { color: #d63031; font-size: 14px; font-weight: bold; }
"""

DARK_STYLE = """
QMainWindow { background-color: #2d3436; color: #dfe6e9; }
QTabWidget::pane { border: 1px solid #636e72; border-radius: 6px; background: #353b48; }
QTabBar::tab { background: #636e72; color: #dfe6e9; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; font-size: 13px; }
QTabBar::tab:selected { background: #0984e3; color: white; font-weight: bold; }
QPushButton { background-color: #0984e3; color: white; border: none; padding: 8px 20px; border-radius: 4px; font-size: 13px; }
QPushButton:hover { background-color: #74b9ff; }
QPushButton#danger { background-color: #d63031; }
QPushButton#danger:hover { background-color: #e17055; }
QPushButton#success { background-color: #00b894; }
QPushButton#success:hover { background-color: #55efc4; }
QTableWidget { gridline-color: #636e72; border: 1px solid #636e72; border-radius: 4px; font-size: 13px; background: #353b48; color: #dfe6e9; }
QTableWidget::item:selected { background-color: #0984e3; color: white; }
QHeaderView::section { background-color: #0984e3; color: white; padding: 6px; border: none; font-weight: bold; }
QGroupBox { font-weight: bold; border: 1px solid #636e72; border-radius: 6px; margin-top: 10px; padding-top: 15px; color: #dfe6e9; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox { padding: 6px; border: 1px solid #636e72; border-radius: 4px; font-size: 13px; background: #353b48; color: #dfe6e9; }
QLabel { color: #dfe6e9; }
QLabel#title { font-size: 18px; font-weight: bold; color: #dfe6e9; padding: 8px; }
QLabel#total { font-size: 20px; font-weight: bold; color: #ff7675; }
QLabel#status_green { color: #55efc4; font-size: 14px; font-weight: bold; }
QLabel#status_yellow { color: #ffeaa7; font-size: 14px; font-weight: bold; }
QLabel#status_red { color: #ff7675; font-size: 14px; font-weight: bold; }
"""


class Database:
    """SQLite 数据库管理"""

    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                icon TEXT DEFAULT '',
                is_default INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY,
                monthly_budget REAL NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        existing = c.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if existing == 0:
            for cat in DEFAULT_CATEGORIES:
                c.execute("INSERT INTO categories (name, is_default) VALUES (?, 1)", (cat,))
        self.conn.commit()

    def add_expense(self, amount, category, description, expense_date):
        self.conn.execute(
            "INSERT INTO expenses (amount, category, description, date, created_at) VALUES (?, ?, ?, ?, ?)",
            (amount, category, description, expense_date, datetime.now().isoformat())
        )
        self.conn.commit()

    def delete_expense(self, expense_id):
        self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()

    def get_all_expenses(self):
        return self.conn.execute(
            "SELECT id, amount, category, description, date FROM expenses ORDER BY date DESC"
        ).fetchall()

    def get_expenses_by_month(self, year, month):
        return self.conn.execute(
            "SELECT id, amount, category, description, date FROM expenses WHERE date LIKE ? ORDER BY date DESC",
            (f"{year}-{month:02d}%",)
        ).fetchall()

    def get_category_totals(self, year=None, month=None):
        if year and month:
            return self.conn.execute(
                "SELECT category, SUM(amount) as total FROM expenses WHERE date LIKE ? GROUP BY category ORDER BY total DESC",
                (f"{year}-{month:02d}%",)
            ).fetchall()
        return self.conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC"
        ).fetchall()

    def get_monthly_total(self, year, month):
        row = self.conn.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE date LIKE ?",
            (f"{year}-{month:02d}%",)
        ).fetchone()
        return row["total"] if row["total"] else 0.0

    def get_all_categories(self):
        return self.conn.execute("SELECT id, name, is_default FROM categories ORDER BY id").fetchall()

    def get_active_category_names(self):
        return [row["name"] for row in self.get_all_categories()]

    def add_category(self, name):
        self.conn.execute("INSERT INTO categories (name, is_default) VALUES (?, 0)", (name,))
        self.conn.commit()

    def delete_category(self, cat_id):
        self.conn.execute("DELETE FROM categories WHERE id = ? AND is_default = 0", (cat_id,))
        self.conn.commit()

    def set_budget(self, amount):
        existing = self.conn.execute("SELECT id FROM budget WHERE id = 1").fetchone()
        if existing:
            self.conn.execute("UPDATE budget SET monthly_budget = ? WHERE id = 1", (amount,))
        else:
            self.conn.execute("INSERT INTO budget (id, monthly_budget) VALUES (1, ?)", (amount,))
        self.conn.commit()

    def get_budget(self):
        row = self.conn.execute("SELECT monthly_budget FROM budget WHERE id = 1").fetchone()
        return row["monthly_budget"] if row else None

    def get_setting(self, key, default=None):
        row = self.conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key, value):
        existing = self.conn.execute("SELECT key FROM settings WHERE key = ?", (key,)).fetchone()
        if existing:
            self.conn.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
        else:
            self.conn.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def close(self):
        self.conn.close()


class PieChartWidget(FigureCanvas):
    """matplotlib 饼图组件"""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 3), dpi=80)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_chart(self, labels, values, dark_mode=False):
        self.ax.clear()
        if not labels or not values or sum(values) == 0:
            self.ax.text(0.5, 0.5, "暂无数据", ha="center", va="center", fontsize=14,
                         color="white" if dark_mode else "#2d3436")
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.draw()
            return

        colors = ["#0984e3", "#00b894", "#fdcb6e", "#d63031", "#6c5ce7", "#e17055", "#00cec9", "#fd79a8"]
        if dark_mode:
            self.ax.set_facecolor("#353b48")
            self.fig.set_facecolor("#353b48")
            text_color = "#dfe6e9"
        else:
            self.ax.set_facecolor("#ffffff")
            self.fig.set_facecolor("#ffffff")
            text_color = "#2d3436"

        wedges, texts, autotexts = self.ax.pie(
            values, labels=labels, autopct="%1.1f%%", colors=colors[:len(labels)],
            startangle=90, textprops={"color": text_color, "fontsize": 9}
        )
        for at in autotexts:
            at.set_fontsize(8)
        self.fig.tight_layout()
        self.draw()


class ExpenseTab(QWidget):
    """记账选项卡"""

    def __init__(self, db, on_expense_added):
        super().__init__()
        self.db = db
        self.on_expense_added = on_expense_added
        self._init_ui()
        self._refresh_categories()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        group = QGroupBox("记录新消费")
        form = QFormLayout()
        form.setSpacing(15)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("¥ ")
        self.amount_input.setFont(QFont("", 12))
        form.addRow("金额:", self.amount_input)

        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont("", 12))
        form.addRow("分类:", self.category_combo)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("可选，如：午饭、打车去图书馆")
        self.desc_input.setFont(QFont("", 12))
        form.addRow("描述:", self.desc_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setFont(QFont("", 12))
        form.addRow("日期:", self.date_input)

        group.setLayout(form)
        layout.addWidget(group)

        btn = QPushButton("记录消费")
        btn.setFont(QFont("", 13, QFont.Bold))
        btn.setMinimumHeight(40)
        btn.clicked.connect(self._submit)
        layout.addWidget(btn)
        layout.addStretch()

    def _refresh_categories(self):
        self.category_combo.clear()
        for name in self.db.get_active_category_names():
            self.category_combo.addItem(name)

    def _submit(self):
        amount = self.amount_input.value()
        category = self.category_combo.currentText()
        description = self.desc_input.text().strip()
        qdate = self.date_input.date()
        expense_date = qdate.toString("yyyy-MM-dd")

        if amount <= 0:
            QMessageBox.warning(self, "警告", "金额必须大于 0")
            return

        self.db.add_expense(amount, category, description, expense_date)
        self.amount_input.setValue(0)
        self.desc_input.clear()
        self.date_input.setDate(QDate.currentDate())
        QMessageBox.information(self, "成功", f"已记录: {category} ¥{amount:.2f}")
        self.on_expense_added()


class RecordsTab(QWidget):
    """消费记录选项卡"""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self._init_ui()
        self.load_all()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("筛选月份:"))

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(date.today().year)
        filter_layout.addWidget(self.year_spin)
        filter_layout.addWidget(QLabel("年"))

        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(date.today().month)
        filter_layout.addWidget(self.month_spin)
        filter_layout.addWidget(QLabel("月"))

        btn_query = QPushButton("查询")
        btn_query.clicked.connect(self._filter)
        filter_layout.addWidget(btn_query)

        btn_all = QPushButton("查看全部")
        btn_all.clicked.connect(self.load_all)
        filter_layout.addWidget(btn_all)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "日期", "分类", "描述", "金额"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_delete = QPushButton("删除选中记录")
        btn_delete.setObjectName("danger")
        btn_delete.clicked.connect(self._delete)
        layout.addWidget(btn_delete)

    def _populate(self, rows):
        self.table.setRowCount(0)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["date"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["category"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["description"] or ""))
            self.table.setItem(i, 4, QTableWidgetItem(f"¥{row['amount']:.2f}"))

    def load_all(self):
        self._populate(self.db.get_all_expenses())

    def _filter(self):
        rows = self.db.get_expenses_by_month(self.year_spin.value(), self.month_spin.value())
        self._populate(rows)

    def _delete(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要删除的记录")
            return
        reply = QMessageBox.question(self, "确认", "确定要删除选中的记录吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        for idx in selected:
            expense_id = int(self.table.item(idx.row(), 0).text())
            self.db.delete_expense(expense_id)
        self.load_all()
        QMessageBox.information(self, "成功", "记录已删除")

    def refresh(self):
        self.load_all()


class StatisticsTab(QWidget):
    """统计选项卡"""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self._init_ui()
        self._update()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("统计月份:"))

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(date.today().year)
        month_layout.addWidget(self.year_spin)
        month_layout.addWidget(QLabel("年"))

        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(date.today().month)
        month_layout.addWidget(self.month_spin)
        month_layout.addWidget(QLabel("月"))

        btn = QPushButton("统计")
        btn.clicked.connect(self._update)
        month_layout.addWidget(btn)
        month_layout.addStretch()
        layout.addLayout(month_layout)

        self.total_label = QLabel("本月消费总额: ¥0.00")
        self.total_label.setObjectName("total")
        self.total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_label)

        splitter = QSplitter(Qt.Horizontal)

        self.stat_table = QTableWidget()
        self.stat_table.setColumnCount(3)
        self.stat_table.setHorizontalHeaderLabels(["分类", "金额", "占比"])
        self.stat_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stat_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stat_table.setAlternatingRowColors(True)
        splitter.addWidget(self.stat_table)

        self.chart = PieChartWidget()
        splitter.addWidget(self.chart)
        splitter.setSizes([400, 400])

        layout.addWidget(splitter)

    def _update(self):
        year, month = self.year_spin.value(), self.month_spin.value()
        total = self.db.get_monthly_total(year, month)
        self.total_label.setText(f"{year}年{month}月消费总额: ¥{total:.2f}")

        cat_data = self.db.get_category_totals(year, month)
        self.stat_table.setRowCount(0)
        self.stat_table.setRowCount(len(cat_data))

        labels, values = [], []
        for i, row in enumerate(cat_data):
            cat, amount = row["category"], row["total"]
            pct = (amount / total * 100) if total > 0 else 0
            self.stat_table.setItem(i, 0, QTableWidgetItem(cat))
            self.stat_table.setItem(i, 1, QTableWidgetItem(f"¥{amount:.2f}"))
            self.stat_table.setItem(i, 2, QTableWidgetItem(f"{pct:.1f}%"))
            labels.append(cat)
            values.append(amount)

        if not cat_data:
            self.stat_table.setRowCount(1)
            self.stat_table.setItem(0, 0, QTableWidgetItem("暂无数据"))
            self.stat_table.setItem(0, 1, QTableWidgetItem(""))
            self.stat_table.setItem(0, 2, QTableWidgetItem(""))

        self.chart.update_chart(labels, values)

    def refresh(self):
        self._update()


class BudgetTab(QWidget):
    """预算选项卡"""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self._init_ui()
        self._load()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        group = QGroupBox("设置月度预算")
        form = QHBoxLayout()
        form.addWidget(QLabel("预算金额:"))

        self.budget_input = QDoubleSpinBox()
        self.budget_input.setRange(0.01, 999999.99)
        self.budget_input.setDecimals(2)
        self.budget_input.setPrefix("¥ ")
        self.budget_input.setFont(QFont("", 12))
        form.addWidget(self.budget_input)

        btn = QPushButton("保存")
        btn.setObjectName("success")
        btn.clicked.connect(self._save)
        form.addWidget(btn)
        form.addStretch()
        group.setLayout(form)
        layout.addWidget(group)

        self.status_label = QLabel("当前预算: 未设置")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("", 14))
        layout.addWidget(self.status_label)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setFont(QFont("", 13, QFont.Bold))
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        layout.addStretch()

    def _save(self):
        amount = self.budget_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "警告", "预算金额必须大于 0")
            return
        self.db.set_budget(amount)
        self._load()
        QMessageBox.information(self, "成功", f"月度预算已设置为 ¥{amount:.2f}")

    def _load(self):
        budget = self.db.get_budget()
        if budget is None:
            self.status_label.setText("当前预算: 未设置")
            self.progress_label.setText("")
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet("")
            return

        self.budget_input.setValue(budget)
        self.status_label.setText(f"当前月度预算: ¥{budget:.2f}")

        today = date.today()
        spent = self.db.get_monthly_total(today.year, today.month)
        remaining = budget - spent
        pct = (spent / budget * 100) if budget > 0 else 0

        bar_value = min(int(pct), 100)
        self.progress_bar.setValue(bar_value)

        if remaining < 0:
            self.progress_label.setText(f"本月已超支 ¥{abs(remaining):.2f}！已使用 {pct:.1f}%")
            self.progress_label.setObjectName("status_red")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #d63031; }")
        elif pct > 80:
            self.progress_label.setText(f"本月已使用 {pct:.1f}%，剩余 ¥{remaining:.2f}，注意控制开支")
            self.progress_label.setObjectName("status_yellow")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #fdcb6e; }")
        else:
            self.progress_label.setText(f"本月已使用 {pct:.1f}%，剩余 ¥{remaining:.2f}")
            self.progress_label.setObjectName("status_green")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #00b894; }")

        self.progress_label.style().unpolish(self.progress_label)
        self.progress_label.style().polish(self.progress_label)

    def refresh(self):
        self._load()


class SettingsTab(QWidget):
    """设置选项卡：自定义分类、数据导出、主题切换"""

    def __init__(self, db, on_theme_changed, on_category_changed):
        super().__init__()
        self.db = db
        self.on_theme_changed = on_theme_changed
        self.on_category_changed = on_category_changed
        self._init_ui()
        self._load_categories()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        cat_group = QGroupBox("自定义分类管理")
        cat_layout = QVBoxLayout()

        add_layout = QHBoxLayout()
        self.new_cat_input = QLineEdit()
        self.new_cat_input.setPlaceholderText("输入新分类名称")
        add_layout.addWidget(self.new_cat_input)
        btn_add = QPushButton("添加分类")
        btn_add.setObjectName("success")
        btn_add.clicked.connect(self._add_category)
        add_layout.addWidget(btn_add)
        cat_layout.addLayout(add_layout)

        self.cat_table = QTableWidget()
        self.cat_table.setColumnCount(3)
        self.cat_table.setHorizontalHeaderLabels(["分类名称", "类型", "操作"])
        self.cat_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cat_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.cat_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        cat_layout.addWidget(self.cat_table)

        btn_delete_cat = QPushButton("删除选中分类")
        btn_delete_cat.setObjectName("danger")
        btn_delete_cat.clicked.connect(self._delete_category)
        cat_layout.addWidget(btn_delete_cat)

        cat_group.setLayout(cat_layout)
        layout.addWidget(cat_group)

        export_group = QGroupBox("数据导出")
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("导出所有消费记录为 CSV 文件"))
        btn_export = QPushButton("导出 CSV")
        btn_export.clicked.connect(self._export_csv)
        export_layout.addWidget(btn_export)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        theme_group = QGroupBox("外观设置")
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["亮色主题", "暗色主题"])
        current = self.db.get_setting("theme", "light")
        self.theme_combo.setCurrentIndex(0 if current == "light" else 1)
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        layout.addStretch()

    def _load_categories(self):
        cats = self.db.get_all_categories()
        self.cat_table.setRowCount(0)
        self.cat_table.setRowCount(len(cats))
        for i, cat in enumerate(cats):
            self.cat_table.setItem(i, 0, QTableWidgetItem(cat["name"]))
            type_text = "默认分类" if cat["is_default"] else "自定义"
            self.cat_table.setItem(i, 1, QTableWidgetItem(type_text))
            btn = QPushButton("删除")
            btn.setObjectName("danger")
            btn.setEnabled(not bool(cat["is_default"]))
            btn.clicked.connect(lambda checked, cid=cat["id"]: self._delete_category_by_id(cid))
            self.cat_table.setCellWidget(i, 2, btn)

    def _add_category(self):
        name = self.new_cat_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "分类名不能为空")
            return
        existing = [c["name"] for c in self.db.get_all_categories()]
        if name in existing:
            QMessageBox.warning(self, "警告", f"分类 '{name}' 已存在")
            return
        self.db.add_category(name)
        self.new_cat_input.clear()
        self._load_categories()
        self.on_category_changed()
        QMessageBox.information(self, "成功", f"已添加分类: {name}")

    def _delete_category(self):
        row = self.cat_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的分类")
            return
        cat_id = self.db.get_all_categories()[row]["id"]
        self._delete_category_by_id(cat_id)

    def _delete_category_by_id(self, cat_id):
        reply = QMessageBox.question(self, "确认", "确定要删除此分类吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self.db.delete_category(cat_id)
        self._load_categories()
        self.on_category_changed()
        QMessageBox.information(self, "成功", "分类已删除")

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出 CSV", "expenses.csv", "CSV Files (*.csv)")
        if not path:
            return
        rows = self.db.get_all_expenses()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "日期", "分类", "描述", "金额"])
            for row in rows:
                writer.writerow([row["id"], row["date"], row["category"], row["description"] or "", f"{row['amount']:.2f}"])
        QMessageBox.information(self, "成功", f"已导出 {len(rows)} 条记录到:\n{path}")

    def _change_theme(self, index):
        theme = "light" if index == 0 else "dark"
        self.db.set_setting("theme", theme)
        self.on_theme_changed(theme)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("校园消费记账系统")
        self.setMinimumSize(900, 650)

        self.db = Database()
        self._apply_theme(self.db.get_setting("theme", "light"))
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        title = QLabel("校园消费记账系统")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.tabs = QTabWidget()
        self.expense_tab = ExpenseTab(self.db, self._on_expense_added)
        self.records_tab = RecordsTab(self.db)
        self.stats_tab = StatisticsTab(self.db)
        self.budget_tab = BudgetTab(self.db)
        self.settings_tab = SettingsTab(self.db, self._apply_theme, self._on_category_changed)

        self.tabs.addTab(self.expense_tab, "  记账  ")
        self.tabs.addTab(self.records_tab, "  消费记录  ")
        self.tabs.addTab(self.stats_tab, "  统计  ")
        self.tabs.addTab(self.budget_tab, "  预算  ")
        self.tabs.addTab(self.settings_tab, "  设置  ")

        self.tabs.currentChanged.connect(self._on_tab_changed)
        main_layout.addWidget(self.tabs)

    def _on_tab_changed(self, index):
        if index == 1:
            self.records_tab.refresh()
        elif index == 2:
            self.stats_tab.refresh()
        elif index == 3:
            self.budget_tab.refresh()

    def _on_expense_added(self):
        self.records_tab.refresh()

    def _on_category_changed(self):
        self.expense_tab._refresh_categories()

    def _apply_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
