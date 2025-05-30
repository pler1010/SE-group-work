import sqlite3

# 数据库初始化函数
def init_database(db):
    # 使用sqlite3创建表
    cursor = db.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'passenger',
        air_temperature_preference REAL,         -- 空调温度偏好，可为空
        music_preference INTEGER,                -- 歌曲喜好（编号，从1开始），可为空
        window_preference TEXT CHECK (window_preference IN ('half', 'full') OR window_preference IS NULL) -- 车窗偏好，可为空，限制为'hafl'或'full'
    )
    ''')
    
    # 创建交互日志表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interaction_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        interaction_type TEXT NOT NULL,
        action TEXT NOT NULL,
        success INTEGER DEFAULT 1,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
    db.commit()
