"""数据库初始化：创建会话表 + 预置业务示例数据"""

import sqlite3
from config import DATA_DIR
from db.session_store import init_session_db


def init_business_db():
    """创建示例销售数据库"""
    db_path = DATA_DIR / "business.db"
    if db_path.exists():
        return

    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        sale_date TEXT NOT NULL,
        region TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        salary REAL NOT NULL,
        hire_date TEXT NOT NULL
    );

    INSERT OR IGNORE INTO products (id, name, category, price) VALUES
        (1, '笔记本电脑', '电子产品', 5999.00),
        (2, '机械键盘', '电子产品', 399.00),
        (3, '运动鞋', '服装', 599.00),
        (4, 'T恤', '服装', 99.00),
        (5, '咖啡豆', '食品', 89.00),
        (6, '牛奶', '食品', 15.00),
        (7, '显示器', '电子产品', 2499.00),
        (8, '书包', '日用品', 199.00),
        (9, '鼠标', '电子产品', 149.00),
        (10, '耳机', '电子产品', 799.00);

    INSERT OR IGNORE INTO sales (id, product_id, quantity, sale_date, region) VALUES
        (1, 1, 5, '2024-01-15', '华东'),
        (2, 2, 20, '2024-01-16', '华东'),
        (3, 3, 15, '2024-01-17', '华南'),
        (4, 4, 50, '2024-01-18', '华南'),
        (5, 5, 30, '2024-01-19', '华北'),
        (6, 6, 100, '2024-01-20', '华北'),
        (7, 1, 3, '2024-02-01', '华南'),
        (8, 7, 8, '2024-02-02', '华东'),
        (9, 2, 25, '2024-02-03', '华北'),
        (10, 3, 10, '2024-02-04', '华东'),
        (11, 4, 40, '2024-02-05', '华南'),
        (12, 5, 20, '2024-02-06', '华北'),
        (13, 8, 35, '2024-02-07', '华东'),
        (14, 1, 7, '2024-03-01', '华北'),
        (15, 6, 80, '2024-03-02', '华南'),
        (16, 7, 12, '2024-03-03', '华东'),
        (17, 2, 18, '2024-03-04', '华南'),
        (18, 5, 25, '2024-03-05', '华东'),
        (19, 4, 60, '2024-03-06', '华北'),
        (20, 3, 22, '2024-03-07', '华南'),
        (21, 9, 40, '2024-01-10', '华东'),
        (22, 10, 15, '2024-01-25', '华南'),
        (23, 9, 30, '2024-02-15', '华北'),
        (24, 10, 20, '2024-02-20', '华东'),
        (25, 1, 10, '2024-03-15', '华东'),
        (26, 7, 5, '2024-03-18', '华南'),
        (27, 10, 25, '2024-03-20', '华北'),
        (28, 2, 35, '2024-03-22', '华东'),
        (29, 3, 18, '2024-03-25', '华南'),
        (30, 6, 120, '2024-03-28', '华北');

    INSERT OR IGNORE INTO employees (id, name, department, salary, hire_date) VALUES
        (1, '张三', '技术部', 15000, '2022-03-15'),
        (2, '李四', '技术部', 18000, '2021-07-01'),
        (3, '王五', '市场部', 12000, '2023-01-10'),
        (4, '赵六', '市场部', 13000, '2022-09-20'),
        (5, '钱七', '销售部', 10000, '2023-06-01'),
        (6, '孙八', '销售部', 11000, '2022-12-15'),
        (7, '周九', '技术部', 20000, '2020-05-01'),
        (8, '吴十', '人事部', 9000, '2023-03-01'),
        (9, '郑十一', '财务部', 14000, '2021-11-01'),
        (10, '冯十二', '技术部', 16000, '2022-06-15');
    """)
    conn.commit()
    conn.close()


def init_all():
    """初始化所有数据库"""
    init_session_db()
    init_business_db()


if __name__ == "__main__":
    init_all()
    print("数据库初始化完成")
