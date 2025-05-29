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
        if self.role == 'driver':
            return True
        else:
            if not self._permissions:
                self._permissions = get_permissions_by_role(self.role)
            return self._permissions.get(action, False)

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

def get_permissions_by_role(role):
    """获取角色权限"""
    db = get_db()
    permission = db.execute('SELECT * FROM permission WHERE role = ?', (role,)).fetchone()
    if permission:
        return {
            'control_ac': bool(permission['control_ac']),
            'control_music': bool(permission['control_music']),
            'control_navigation': bool(permission['control_navigation']),
            'system_settings': bool(permission['system_settings'])
        }
    return {}

def log_interaction(user_id, interaction_type, action, success=True, details=None):
    """记录交互日志"""
    db = get_db()
    db.execute(
        'INSERT INTO interaction_log (user_id, interaction_type, action, success, details) VALUES (?, ?, ?, ?, ?)',
        (user_id, interaction_type, action, 1 if success else 0, details)
    )
    db.commit()

def save_user_preference(user_id, preference_type, preference_key, preference_value):
    """保存用户偏好设置"""
    db = get_db()
    existing = db.execute(
        'SELECT * FROM user_preference WHERE user_id = ? AND preference_type = ? AND preference_key = ?',
        (user_id, preference_type, preference_key)
    ).fetchone()
    
    if existing:
        db.execute(
            'UPDATE user_preference SET preference_value = ?, updated_at = ? WHERE id = ?',
            (preference_value, datetime.datetime.now(), existing['id'])
        )
    else:
        db.execute(
            'INSERT INTO user_preference (user_id, preference_type, preference_key, preference_value) VALUES (?, ?, ?, ?)',
            (user_id, preference_type, preference_key, preference_value)
        )
    db.commit()
