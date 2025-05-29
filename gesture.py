from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import numpy as np
import cv2
from db_utils import get_user_by_id, log_interaction

gesture_bp = Blueprint('gesture', __name__)

# 预定义手势及其动作
GESTURES = {
    "fist": {
        "action": "pause_music", 
        "description": "握拳暂停音乐", 
        "requires_permission": "control_music"
    },
    "thumbs_up": {
        "action": "confirm", 
        "description": "竖起大拇指确认", 
        "requires_permission": None  # 所有用户都可以使用
    },
    "wave": {
        "action": "reject", 
        "description": "摇手表示拒绝", 
        "requires_permission": None  # 所有用户都可以使用
    }
}

@gesture_bp.route('/gesture')
def gesture_interface():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    return render_template('multimodal.html')

@gesture_bp.route('/process_gesture', methods=['POST'])
def process_gesture():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "用户未登录"})
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"success": False, "message": "无效的用户"})
    
    # 在实际应用中，这里会接收图像数据并进行手势识别
    # 为了演示，我们简化为直接接收已识别的手势名称
    
    if 'image' in request.files:
        # 处理上传的图像文件
        image_file = request.files['image']
        image_array = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # 这里应该是实际的手势识别代码
        # 为了简化，我们返回一个模拟的识别结果
        gesture = detect_gesture(image)
    else:
        # 直接接收识别结果（用于测试）
        gesture = request.form.get('gesture', '')
    
    if gesture in GESTURES:
        details = GESTURES[gesture]
        
        # 检查权限
        if details["requires_permission"] is None or current_user.has_permission(details["requires_permission"]):
            response = {
                "success": True,
                "message": f"检测到手势: {details['description']}",
                "action": details["action"]
            }
            
            # 记录交互日志
            log_interaction(
                user_id=current_user.id,
                interaction_type="gesture",
                action=details["action"],
                success=True,
                details=f"Detected gesture: {gesture}"
            )
        else:
            response = {
                "success": False,
                "message": "您没有执行此手势命令的权限",
                "action": None
            }
    else:
        response = {
            "success": False,
            "message": "未识别的手势",
            "action": None
        }
    
    return jsonify(response)

def detect_gesture(image):
    """
    手势识别函数（实际应用中需要实现真正的手势识别算法）
    这里只是简单模拟返回一个随机手势
    """
    # 实际应用中这里应该有基于深度学习或计算机视觉的手势识别逻辑
    import random
    return random.choice(list(GESTURES.keys()) + ["unknown"] * 2)  # 增加未识别的概率
