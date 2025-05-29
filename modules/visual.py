from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import numpy as np
import cv2
from db_utils import get_user_by_id, log_interaction

visual_bp = Blueprint('visual', __name__)

# 预定义视觉动作
VISUAL_ACTIONS = {
    "nod": {
        "action": "confirm", 
        "description": "点头确认", 
        "requires_permission": None
    },
    "shake": {
        "action": "reject", 
        "description": "摇头拒绝", 
        "requires_permission": None
    },
    "gaze_center": {
        "action": "select_center", 
        "description": "注视中央",
        "requires_permission": None
    },
    "gaze_left": {
        "action": "select_left", 
        "description": "注视左侧", 
        "requires_permission": None
    },
    "gaze_right": {
        "action": "select_right", 
        "description": "注视右侧", 
        "requires_permission": None
    }
}

@visual_bp.route('/process_head_pose', methods=['POST'])
def process_head_pose():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "用户未登录"})
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"success": False, "message": "无效的用户"})
    
    if 'image' in request.files:
        # 处理上传的图像
        image_file = request.files['image']
        image_array = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # 进行头部姿态识别
        pose = detect_head_pose(image)
    else:
        # 直接接收识别结果（用于测试）
        pose = request.form.get('pose', '')
    
    if pose in ["nod", "shake"]:
        details = VISUAL_ACTIONS[pose]
        
        response = {
            "success": True,
            "message": f"检测到头部姿态: {details['description']}",
            "action": details["action"]
        }
        
        # 记录交互日志
        log_interaction(
            user_id=current_user.id,
            interaction_type="visual",
            action=details["action"],
            success=True,
            details=f"Detected head pose: {pose}"
        )
    else:
        response = {
            "success": False,
            "message": "未识别的头部姿态",
            "action": None
        }
    
    return jsonify(response)

@visual_bp.route('/process_gaze', methods=['POST'])
def process_gaze():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "用户未登录"})
    
    current_user = get_user_by_id(session['user_id'])
    if not current_user:
        return jsonify({"success": False, "message": "无效的用户"})
    
    # 在实际应用中，这里会接收图像数据并进行目光跟踪
    
    if 'image' in request.files:
        # 处理上传的图像
        image_file = request.files['image']
        image_array = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # 进行目光跟踪
        gaze_direction = detect_gaze(image)
    else:
        # 直接接收识别结果（用于测试）
        gaze_direction = request.form.get('gaze', '')
    
    gaze_key = f"gaze_{gaze_direction}" if gaze_direction in ["center", "left", "right"] else None
    
    if gaze_key and gaze_key in VISUAL_ACTIONS:
        details = VISUAL_ACTIONS[gaze_key]
        
        response = {
            "success": True,
            "message": f"检测到目光方向: {details['description']}",
            "action": details["action"],
            "direction": gaze_direction
        }
        
        # 记录交互日志
        log_interaction(
            user_id=current_user.id,
            interaction_type="visual",
            action=details["action"],
            success=True,
            details=f"Detected gaze: {gaze_direction}"
        )
    else:
        response = {
            "success": False,
            "message": "未识别的目光方向",
            "action": None,
            "direction": None
        }
    
    return jsonify(response)

@visual_bp.route('/visual')
def visual_interface():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    return render_template('multimodal.html')

def detect_head_pose(image):
    """
    头部姿态识别函数（实际应用中需要实现真正的头部姿态检测）
    """
    # 实际应用中这里应该使用OpenCV或深度学习模型来检测头部姿态
    import random
    return random.choice(["nod", "shake", "unknown"])

def detect_gaze(image):
    """
    目光方向检测函数（实际应用中需要实现真正的目光跟踪算法）
    """
    # 实际应用中这里应该使用专门的目光跟踪算法
    import random
    return random.choice(["center", "left", "right", "unknown"])
