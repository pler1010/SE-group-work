from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from db_utils import get_user_by_id, save_user_preference, get_db

system_bp = Blueprint('system', __name__)

@system_bp.route('/preferences')
def preferences():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return redirect(url_for('auth.login'))
    
    # 使用SQLite直接查询而不是使用SQLAlchemy
    db = get_db()
    user_preferences = db.execute(
        'SELECT * FROM user_preference WHERE user_id = ?', 
        (current_user.id,)
    ).fetchall()
    
    return render_template('preferences.html', preferences=user_preferences)

@system_bp.route('/save_preference', methods=['POST'])
def save_preference():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "用户未登录"})
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"success": False, "message": "无效的用户"})
    
    preference_type = request.form.get('type')
    preference_key = request.form.get('key')
    preference_value = request.form.get('value')
    
    # 使用自定义函数保存偏好
    save_user_preference(
        current_user.id, 
        preference_type, 
        preference_key, 
        preference_value
    )
    
    return jsonify({"success": True})

@system_bp.route('/logs')
def logs():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user or current_user.role != 'driver':
        return redirect(url_for('index'))
    
    # 使用SQLite直接查询
    db = get_db()
    logs = db.execute(
        'SELECT * FROM interaction_log ORDER BY created_at DESC LIMIT 100'
    ).fetchall()
    
    # 统计
    voice_count = db.execute(
        'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "voice"'
    ).fetchone()['count']
    
    gesture_count = db.execute(
        'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "gesture"'
    ).fetchone()['count']
    
    visual_count = db.execute(
        'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "visual"'
    ).fetchone()['count']
    
    success_rate = db.execute(
        'SELECT COUNT(*) as total, SUM(success) as success_count FROM interaction_log'
    ).fetchone()
    
    if success_rate['total'] > 0:
        success_percentage = (success_rate['success_count'] / success_rate['total']) * 100
    else:
        success_percentage = 0
    
    stats = {
        'voice_count': voice_count,
        'gesture_count': gesture_count,
        'visual_count': visual_count,
        'total': voice_count + gesture_count + visual_count,
        'success_rate': round(success_percentage, 2)
    }
    
    return render_template('logs.html', logs=logs, stats=stats)

@system_bp.route('/permissions')
def permissions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user or current_user.role != 'driver':
        return redirect(url_for('index'))
    
    # 使用SQLite直接查询
    db = get_db()
    driver_permissions = db.execute(
        'SELECT * FROM permission WHERE role = "driver"'
    ).fetchone()
    
    passenger_permissions = db.execute(
        'SELECT * FROM permission WHERE role = "passenger"'
    ).fetchone()
    
    # 如果不存在则创建默认权限
    if not driver_permissions:
        db.execute(
            'INSERT INTO permission (role, control_ac, control_music, control_navigation, system_settings) VALUES (?, ?, ?, ?, ?)',
            ('driver', 1, 1, 1, 1)
        )
        db.commit()
        driver_permissions = db.execute('SELECT * FROM permission WHERE role = "driver"').fetchone()
    
    if not passenger_permissions:
        db.execute(
            'INSERT INTO permission (role, control_ac, control_music, control_navigation, system_settings) VALUES (?, ?, ?, ?, ?)',
            ('passenger', 0, 1, 0, 0)
        )
        db.commit()
        passenger_permissions = db.execute('SELECT * FROM permission WHERE role = "passenger"').fetchone()
    
    return render_template('permissions.html', driver=driver_permissions, passenger=passenger_permissions)

@system_bp.route('/update_permissions', methods=['POST'])
def update_permissions():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "用户未登录"})
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user or current_user.role != 'driver':
        return jsonify({"success": False, "message": "无权更新权限"})
    
    role = request.form.get('role')
    if role not in ['driver', 'passenger']:
        return jsonify({"success": False, "message": "无效的角色"})
    
    # 获取权限设置
    control_ac = 1 if request.form.get('control_ac') == 'on' else 0
    control_music = 1 if request.form.get('control_music') == 'on' else 0
    control_navigation = 1 if request.form.get('control_navigation') == 'on' else 0
    system_settings = 1 if request.form.get('system_settings') == 'on' else 0
    
    db = get_db()
    db.execute(
        'UPDATE permission SET control_ac=?, control_music=?, control_navigation=?, system_settings=? WHERE role=?',
        (control_ac, control_music, control_navigation, system_settings, role)
    )
    db.commit()
    
    return jsonify({"success": True, "message": f"{role}角色权限已更新"})

@system_bp.route('/simulate_distraction', methods=['POST'])
def simulate_distraction():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "用户未登录"})

    # 模拟分心状态触发
    return jsonify({"success": True, "message": "警告! 请目视前方", "color": "red"})
