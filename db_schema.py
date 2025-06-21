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
        window_preference TEXT CHECK (window_preference IN ('half', 'full') OR window_preference IS NULL) -- 车窗偏好，可为空，限制为'half'或'full'
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
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
    # 检查是否需要更新 created_at 字段格式
    cursor.execute("PRAGMA table_info(interaction_log)")
    columns = cursor.fetchall()
    
    # 查找 created_at 列的信息
    created_at_column = None
    for column in columns:
        if column[1] == 'created_at':  # column[1] 是列名
            created_at_column = column
            break
    
    # 如果 created_at 列的默认值不正确，我们可能需要更新现有数据
    # 但为了简单起见，我们就保持现状，让应用层处理格式转换
    
    db.commit()
    print("数据库表已创建/更新")