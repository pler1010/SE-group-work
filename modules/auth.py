from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from db_utils import get_user_by_username, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))  # 登录后重定向到主页
        else:
            flash('用户名或密码无效')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'passenger')
        
        existing_user = get_user_by_username(username)
        if existing_user:
            flash('用户名已存在')
        else:
            new_user = create_user(username, password, role)
            if new_user:
                session['user_id'] = new_user.id
                return redirect(url_for('index'))
            else:
                flash('创建用户失败，请重试')
            
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))
