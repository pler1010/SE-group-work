import sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User:
    """用户类，实现用户所需的基本方法"""
    def __init__(self, id, username, password, role,
                 air_temperature_preference=None,
                 music_preference=None,
                 window_preference=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        # 用户偏好
        self.air_temperature_preference = air_temperature_preference
        self.music_preference = music_preference
        self.window_preference = window_preference

    def get_id(self):
        return str(self.id)

    def has_permission(self, action):
        # 权限系统简化，可根据角色添加判断逻辑
        return True


def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def get_user_by_id(user_id):
    """根据ID获取用户"""
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(
            user['id'],
            user['username'],
            user['password'],
            user['role'],
            user['air_temperature_preference'],
            user['music_preference'],
            user['window_preference']
        )
    return None


def get_user_by_username(username):
    """根据用户名获取用户"""
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
    if user:
        return User(
            user['id'],
            user['username'],
            user['password'],
            user['role'],
            user['air_temperature_preference'],
            user['music_preference'],
            user['window_preference']
        )
    return None

def create_user(username, password, role='passenger',
                air_temperature_preference=None,
                music_preference=None,
                window_preference=None):
    """创建新用户，包含偏好设置"""
    db = get_db()
    try:
        db.execute(
            '''
            INSERT INTO user (username, password, role,
                              air_temperature_preference,
                              music_preference,
                              window_preference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                username,
                generate_password_hash(password),
                role,
                air_temperature_preference,
                music_preference,
                window_preference
            )
        )
        db.commit()
        return get_user_by_username(username)
    except sqlite3.IntegrityError:
        return None

def log_interaction(user_id, interaction_type, action, success=True, details=None):
    """记录交互日志"""
    db = get_db()
    db.execute(
        'INSERT INTO interaction_log (user_id, interaction_type, action, success, details) VALUES (?, ?, ?, ?, ?)',
        (user_id, interaction_type, action, 1 if success else 0, details)
    )
    db.commit()
