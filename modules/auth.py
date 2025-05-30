from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from db_utils import get_user_by_username, create_user
from deepface import DeepFace
import os

FACE_DIR = 'faces/'
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        face_image = request.files.get('face_image')

        if username and password:
            user = get_user_by_username(username)
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect(url_for('index'))
            else:
                flash('用户名或密码无效')

        elif face_image:
            temp_path = 'temp_login.jpg'
            face_image.save(temp_path)

            for file in os.listdir(FACE_DIR):
                user_image_path = os.path.join(FACE_DIR, file)
                try:
                    result = DeepFace.verify(temp_path, user_image_path, enforce_detection=False)
                    if result["verified"]:
                        matched_username = file.split('.')[0]
                        user = get_user_by_username(matched_username)
                        if user:
                            session['user_id'] = user.id
                            os.remove(temp_path)
                            return redirect(url_for('index'))
                except:
                    continue

            os.remove(temp_path)
            flash('人脸识别失败，请重试')
        else:
            flash('请提供用户名密码或人脸数据')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'passenger')
        face_image = request.files.get('face_image')

        # 获取偏好设置，可为空
        air_temp = request.form.get('air_temperature_preference')  # 字符串，需转 float
        music_pref = request.form.get('music_preference')          # 字符串，需转 int
        window_pref = request.form.get('window_preference')        # 可为 'half', 'full' 或 None

        # 类型转换（空字符串视为 None）
        air_temp = float(air_temp) if air_temp else None
        music_pref = int(music_pref) if music_pref else None
        window_pref = window_pref if window_pref in ('half', 'full') else None

        existing_user = get_user_by_username(username)
        if existing_user:
            flash('用户名已存在')
        else:
            new_user = create_user(
                username, password, role,
                air_temperature_preference=air_temp,
                music_preference=music_pref,
                window_preference=window_pref
            )
            if new_user:
                if face_image:
                    image_path = os.path.join(FACE_DIR, f'{username}.jpg')
                    face_image.save(image_path)
                session['user_id'] = new_user.id
                return redirect(url_for('index'))
            else:
                flash('创建用户失败，请重试')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))
