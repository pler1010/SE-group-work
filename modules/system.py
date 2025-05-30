from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from db_utils import get_user_by_id, get_db
from gesture import detect_gesture
from visual import detect_visual
from voice import detect_voice

class State:
    def __init__(self):
        self.air_condition_temperature = '0'
        self.left_window = 'off'
        self.right_window = 'off'
        self.skylight = 'off'
        self.music = '0'
        self.alarm = '0'
    def next_temperature(self,user,ges,voi):
        pass
    def next_window(self,user,ges,voi):
        pass
    def next_music(self,user,ges,voi):
        pass
    def next_alarm(self,vis):
        pass
    def get_next(self,user,ges,vis,voi):
        self.next_temperature(self,user,ges,voi)
        self.next_window(self,user,ges,voi)
        self.next_music(self,user,ges,voi)
        self.next_alarm(self,vis)
def add(list, time, state):
    list.append({
        "time":str(time),
        "air_condition_temperature":state.air_condition_temperature,
        "left_window":state.left_window,
        "right_window":state.right_window,
        "self.skylight":state.skylight,
        "self.music":state.music,
        "self.alarm":state.alarm
        })

system_bp = Blueprint('system', __name__)

@system_bp.route('/control', methods=['POST'])
def control():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"success": False, "message": "无效的用户"})
    
    video = request.files.get('video')
    if not video:
        return jsonify({"error": "No video uploaded"}), 400
    
    gesture_list=detect_gesture(video)
    visual_list=detect_visual(video)
    voice_list=detect_voice(video)
    length = min(len(gesture_list),len(visual_list),len(voice_list))

    result = []
    state=State()
    add(result, state)

    for i in range(length):
        state.get_next(user,gesture_list[i],visual_list[i],voice_list[i])
        add(result,5*i,state)

    return jsonify(result)

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