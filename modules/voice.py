from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from db_utils import log_interaction, get_user_by_id
import json
import os

voice_bp = Blueprint('voice', __name__)

# 预定义的语音命令和对应的动作
VOICE_COMMANDS = {
    "打开空调": {"action": "turn_on_ac", "requires_permission": "control_ac"},
    "关闭空调": {"action": "turn_off_ac", "requires_permission": "control_ac"},
    "调高温度": {"action": "increase_temp", "requires_permission": "control_ac"},
    "调低温度": {"action": "decrease_temp", "requires_permission": "control_ac"},
    "播放音乐": {"action": "play_music", "requires_permission": "control_music"},
    "暂停音乐": {"action": "pause_music", "requires_permission": "control_music"},
    "下一首": {"action": "next_track", "requires_permission": "control_music"},
    "上一首": {"action": "prev_track", "requires_permission": "control_music"},
    "导航到家": {"action": "navigate_home", "requires_permission": "control_navigation"},
    "导航到公司": {"action": "navigate_work", "requires_permission": "control_navigation"}
}

VOICE_COMMANDS.update({
    "已注意道路": {"action": "acknowledge_warning", "requires_permission": None}
})

@voice_bp.route('/voice')
def voice_interface():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    return render_template('multimodal.html')

@voice_bp.route('/process_voice', methods=['POST'])
def process_voice():
    # 在实际应用中，这里会收到语音数据并进行处理
    
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "用户未登录"})
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"success": False, "message": "无效的用户"})
    
    # 直接接收文本（用于测试）
    text = request.form.get('text', '')
    
    # 检查命令是否被识别
    response = {"success": False, "message": "未识别的命令", "action": None}
    
    for command, details in VOICE_COMMANDS.items():
        if command in text:
            # 检查权限
            if current_user.has_permission(details["requires_permission"]):
                response = {
                    "success": True, 
                    "message": f"执行命令: {command}",
                    "action": details["action"]
                }
                
                # 记录交互日志
                log_interaction(
                    user_id=current_user.id,
                    interaction_type="voice",
                    action=details["action"],
                    success=True,
                    details=text
                )
            else:
                response = {
                    "success": False,
                    "message": "您没有执行此命令的权限",
                    "action": None
                }
            break
    
    return jsonify(response)
