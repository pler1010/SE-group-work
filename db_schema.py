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
        role TEXT DEFAULT 'passenger'
    )
    ''')
    
    # 创建用户偏好表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_preference (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        preference_type TEXT NOT NULL,
        preference_key TEXT NOT NULL,
        preference_value TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (id)
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
    
    # 创建权限表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS permission (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT UNIQUE NOT NULL,
        control_ac INTEGER DEFAULT 0,
        control_music INTEGER DEFAULT 1,
        control_navigation INTEGER DEFAULT 0,
        system_settings INTEGER DEFAULT 0
    )
    ''')
    
    # 添加默认权限设置
    cursor.execute('''
    INSERT OR IGNORE INTO permission (role, control_ac, control_music, control_navigation, system_settings)
    VALUES ('driver', 1, 1, 1, 1)
    ''')
    
    cursor.execute('''
    INSERT OR IGNORE INTO permission (role, control_ac, control_music, control_navigation, system_settings)
    VALUES ('passenger', 0, 1, 0, 0)
    ''')
    
    db.commit()
