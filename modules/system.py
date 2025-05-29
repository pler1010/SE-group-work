from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from db_utils import get_user_by_id, save_user_preference, get_db

system_bp = Blueprint('system', __name__)

@system_bp.route('/control', methods=['POST'])
def control():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"success": False, "message": "无效的用户"})

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