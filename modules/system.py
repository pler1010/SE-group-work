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
        self.music = 'stop'
        self.alarm = '0'
    def next_temperature(self,user,ges,voi):
        if '空调' not in voi:
            return

        close = False
        open = False
        if '开' in voi:
            open = True
        if '关' in voi or '停' in voi:
            close =True

        tem = '25'
        if user.air_temperature_preference is not None:
            tem = user.air_temperature_preference
        
        if close and not open:
            self.air_condition_temperature='0'
            return
        if self.air_condition_temperature == '0':
            if open and not close:
                self.air_condition_temperature = tem
                return
        if self.air_condition_temperature != '0':
            if '高' in voi:
                self.air_condition_temperature=str(int(self.air_condition_temperature)+1)
            if '低' in voi:
                self.air_condition_temperature=str(int(self.air_condition_temperature)-1)
    def next_window(self,user,ges,voi):
        open = False
        close = False
        if '开' in voi:
            open = True
        if '关' in voi:
            close = True
        if not open and not close:
            return
        if open and close:
            return
        
        val = 'on' if open else 'off'
        if val=='on' and user.window_preference=='half':
            val='half'

        if '左车窗' in voi:
            self.left_window=val
            return
        if '右车窗' in voi:
            self.right_window=val
            return
        if '天窗' in voi:
            self.skylight=val
            return
        if ges=='up':
            self.skylight=val
            return
        if ges=='left':
            self.left_window=val
            return
        if ges=='right':
            self.right_window=val
            return
        if '车窗' in voi:
            self.left_window=val
            self.right_window=val
    def next_music(self,user,ges,voi):
        if '下一首' in voi:
            self.music='next'
            return
        if '上一首' in voi:
            self.music='pre'
            return
        
        if '音乐' not in voi and '歌' not in voi:
            return
        
        music=''
        if user.music_preference:
            music=str(user.music_preference)

        close = False
        open = False
        if '关' in voi or '停' in voi or ges == 'fist':
            close = True
        if '开' in voi or '听' in voi or '播' in voi or ges == 'palm':
            open = True
        
        if close and not open:
            self.music='stop'
        if open and not close:
            self.music='start'+music
    def next_alarm(self,ges,vis):
        if vis == 'wander':
            if self.alarm == '0':
                self.alarm = '1'
        if vis == 'tired':
            if self.alarm != '3':
                self.alarm = '2'
        if vis == 'sleepy':
            self.alarm = '3'
        if ges == 'thumb':
            self.alarm = '0'
    def get_next(self,user,ges,vis,voi):
        self.next_temperature(user,ges,voi)
        self.next_window(user,ges,voi)
        self.next_music(user,ges,voi)
        self.next_alarm(ges,vis)
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
    add(result,0,state)

    for i in range(length):
        state.get_next(current_user,gesture_list[i],visual_list[i],voice_list[i])
        add(result,5*(i+1),state)

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