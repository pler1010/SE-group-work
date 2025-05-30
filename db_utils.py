import sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User:
    """用户类，实现用户所需的基本方法"""
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self._permissions = None
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)
    
    def has_permission(self, action):
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
        return User(user['id'], user['username'], user['password'], user['role'])
    return None

def get_user_by_username(username):
    """根据用户名获取用户"""
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
    if user:
        return User(user['id'], user['username'], user['password'], user['role'])
    return None

def create_user(username, password, role='passenger'):
    """创建新用户"""
    db = get_db()
    try:
        db.execute(
            'INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
            (username, generate_password_hash(password), role)
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
