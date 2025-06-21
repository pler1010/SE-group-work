from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from db_utils import get_user_by_id, get_db, log_interaction
import os
import traceback

# 如果检测模块导入失败，使用测试数据
try:
    from gesture import detect_gesture
except ImportError:
    print("警告：gesture模块导入失败，使用测试数据")
    def detect_gesture(video):
        return ['none', 'left', 'fist', 'none', 'thumb', 'palm']

try:
    from visual import detect_visual
except ImportError:
    print("警告：visual模块导入失败，使用测试数据")
    def detect_visual(video):
        return ['awake', 'wander', 'tired', 'sleepy', 'awake', 'wander']

try:
    from voice import detect_voice
except ImportError:
    print("警告：voice模块导入失败，使用测试数据")
    def detect_voice(video):
        return ['', '开空调', '关音乐', '', '开左车窗', '播放音乐']

class State:
    def __init__(self):
        self.air_condition_temperature = '0'
        self.left_window = 'off'
        self.right_window = 'off'
        self.skylight = 'off'
        self.music = 'stop'
        self.alarm = '0'
        self.alarm_detail = ''  # 新增：存储具体的警告详情
        
    def next_temperature(self,user,ges,voi):
        if '空调' not in voi:
            return

        close = False
        open = False
        if '开' in voi:
            open = True
        if '关' in voi or '停' in voi:
            close = True

        tem = '25'
        if user.air_temperature_preference is not None:
            tem = str(user.air_temperature_preference)
        
        if close and not open:
            self.air_condition_temperature='0'
            return
        if self.air_condition_temperature == '0':
            if open and not close:
                self.air_condition_temperature = tem
                return
        if self.air_condition_temperature != '0':
            if '高' in voi:
                self.air_condition_temperature=str(int(float(self.air_condition_temperature))+1)
            if '低' in voi:
                self.air_condition_temperature=str(int(float(self.air_condition_temperature))-1)
                
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
            
    def next_alarm(self, ges, vis):
        # 重置警告详情
        self.alarm_detail = ''
        
        if vis == 'wander':
            if self.alarm == '0':
                self.alarm = '1'
                self.alarm_detail = '注意力分散'
                    
        if vis == 'tired':
            if self.alarm != '3':
                self.alarm = '2'
                self.alarm_detail = '疲劳驾驶'
                
        if vis == 'sleepy':
            self.alarm = '3'
            self.alarm_detail = '瞌睡状态'
            
        if ges == 'thumb':
            self.alarm = '0'
            self.alarm_detail = ''
            
    def get_next(self, user, ges, vis, voi):
        self.next_temperature(user, ges, voi)
        self.next_window(user, ges, voi)
        self.next_music(user, ges, voi)
        self.next_alarm(ges, vis)

def add(list, time, state):
    list.append({
        "time": str(time),
        "air_condition_temperature": state.air_condition_temperature,
        "left_window": state.left_window,
        "right_window": state.right_window,
        "skylight": state.skylight,
        "music": state.music,
        "alarm": state.alarm,
        "alarm_detail": state.alarm_detail  # 新增警告详情
    })

# 新增：记录交互日志的辅助函数
def log_interaction_data(user_id, gesture_list, visual_list, voice_list):
    """记录所有检测到的交互数据到数据库"""
    try:
        # 记录手势交互
        for i, gesture in enumerate(gesture_list):
            if gesture != 'none':
                log_interaction(
                    user_id=user_id,
                    interaction_type='gesture',
                    action=f'检测到手势: {gesture}',
                    success=True,
                    details=f'时间段: {i*5}-{(i+1)*5}秒, 手势类型: {gesture}'
                )
        
        # 记录视觉交互
        for i, visual in enumerate(visual_list):
            if visual != 'none':
                log_interaction(
                    user_id=user_id,
                    interaction_type='visual',
                    action=f'检测到状态: {visual}',
                    success=True,
                    details=f'时间段: {i*5}-{(i+1)*5}秒, 状态: {visual}'
                )
        
        # 记录语音交互
        for i, voice in enumerate(voice_list):
            if voice.strip():  # 如果语音不为空
                log_interaction(
                    user_id=user_id,
                    interaction_type='voice',
                    action=f'语音指令: {voice}',
                    success=True,
                    details=f'时间段: {i*5}-{(i+1)*5}秒, 指令内容: {voice}'
                )
        
        print(f"成功记录交互日志: 手势{len([g for g in gesture_list if g != 'none'])}条, "
              f"视觉{len([v for v in visual_list if v != 'none'])}条, "
              f"语音{len([v for v in voice_list if v.strip()])}条")
              
    except Exception as e:
        print(f"记录交互日志时出错: {e}")

system_bp = Blueprint('system', __name__)

@system_bp.route('/test', methods=['GET'])
def test():
    """测试路由，确保后端正常工作"""
    return jsonify({"status": "ok", "message": "后端服务正常"})

@system_bp.route('/control', methods=['POST'])
def control():
    if 'user_id' not in session:
        return jsonify({"error": "用户未登录", "redirect": url_for('auth.login')}), 401
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"error": "无效的用户"}), 400
    
    video = request.files.get('video')
    if not video:
        return jsonify({"error": "没有上传视频文件"}), 400
    
    print(f"收到视频文件: {video.filename}, 大小: {video.content_length}")
    
    # 确保temp目录存在
    if not os.path.exists('temp'):
        os.makedirs('temp')
        print("创建temp目录")
    
    try:
        # 保存临时文件
        temp_path = os.path.join('temp', 'temp_video.mp4')
        video.save(temp_path)
        print(f"视频已保存到: {temp_path}")
        
        # 重新设置文件指针
        video.seek(0)
        
        print("开始手势检测...")
        gesture_list = detect_gesture(video)
        print(f"手势检测结果: {gesture_list}")
        
        print("开始视觉检测...")
        visual_list = detect_visual(video)
        print(f"视觉检测结果: {visual_list}")
        
        print("开始语音检测...")
        voice_list = detect_voice(video)
        print(f"语音检测结果: {voice_list}")
        
        # 新增：记录交互日志到数据库
        log_interaction_data(current_user.id, gesture_list, visual_list, voice_list)
        
        length = min(len(gesture_list), len(visual_list), len(voice_list))
        print(f"最短列表长度: {length}")

        result = []
        state = State()
        add(result, 0, state)

        for i in range(length):
            print(f"处理第{i+1}个时间段...")
            state.get_next(current_user, gesture_list[i], visual_list[i], voice_list[i])
            add(result, 5*(i+1), state)

        # 记录整体分析完成日志
        log_interaction(
            user_id=current_user.id,
            interaction_type='system',
            action='视频分析完成',
            success=True,
            details=f'分析了{length}个时间段的数据，生成{len(result)}个状态节点'
        )

        print(f"最终结果: {result}")
        return jsonify(result)
    
    except Exception as e:
        error_msg = f"处理视频时出错: {str(e)}"
        print(error_msg)
        print("详细错误信息:")
        print(traceback.format_exc())
        
        # 记录错误日志
        try:
            log_interaction(
                user_id=current_user.id,
                interaction_type='system',
                action='视频分析失败',
                success=False,
                details=f'错误信息: {str(e)}'
            )
        except:
            pass  # 如果连日志都记录不了，就忽略
        
        return jsonify({"error": error_msg, "details": traceback.format_exc()}), 500

@system_bp.route('/logs')
def logs():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return redirect(url_for('index'))
    
    # 使用SQLite直接查询
    db = get_db()
    logs_raw = db.execute(
        'SELECT * FROM interaction_log ORDER BY created_at DESC LIMIT 100'
    ).fetchall()
    
    # 转换日志数据，处理日期格式
    logs = []
    for log in logs_raw:
        log_dict = dict(log)
        # 确保 created_at 是正确的格式
        if log_dict['created_at']:
            try:
                from datetime import datetime
                # 如果是字符串，尝试解析
                if isinstance(log_dict['created_at'], str):
                    log_dict['created_at'] = datetime.fromisoformat(log_dict['created_at'].replace('Z', '+00:00'))
                # 如果已经是 datetime 对象，直接使用
            except:
                # 如果解析失败，保持原始字符串
                pass
        logs.append(log_dict)
    
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
    
    system_count = db.execute(
        'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "system"'
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
        'system_count': system_count,
        'total': voice_count + gesture_count + visual_count + system_count,
        'success_rate': round(success_percentage, 2)
    }
    
    return render_template('logs.html', logs=logs, stats=stats)

@system_bp.route('/logs/refresh', methods=['GET'])
def refresh_logs():
    """新增：AJAX刷新日志数据的接口"""
    if 'user_id' not in session:
        return jsonify({"error": "用户未登录"}), 401
    
    try:
        db = get_db()
        logs = db.execute(
            'SELECT * FROM interaction_log ORDER BY created_at DESC LIMIT 50'
        ).fetchall()
        
        # 转换为字典格式，方便JSON序列化
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log['id'],
                'interaction_type': log['interaction_type'],
                'action': log['action'],
                'success': bool(log['success']),
                'details': log['details'] or '',
                'created_at': log['created_at']
            })
        
        # 重新计算统计数据
        voice_count = db.execute(
            'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "voice"'
        ).fetchone()['count']
        
        gesture_count = db.execute(
            'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "gesture"'
        ).fetchone()['count']
        
        visual_count = db.execute(
            'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "visual"'
        ).fetchone()['count']
        
        system_count = db.execute(
            'SELECT COUNT(*) as count FROM interaction_log WHERE interaction_type = "system"'
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
            'system_count': system_count,
            'total': voice_count + gesture_count + visual_count + system_count,
            'success_rate': round(success_percentage, 2)
        }
        
        return jsonify({
            'logs': logs_data,
            'stats': stats,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"刷新日志时出错: {e}")
        return jsonify({"error": f"刷新失败: {str(e)}"}), 500