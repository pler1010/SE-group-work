import click
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
import os
import sys
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'multimodal_secret_key'
app.config['DATABASE'] = os.path.join(app.instance_path, 'multimodal.db')

# 确保实例文件夹存在
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# 数据库连接函数
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 初始化数据库
def init_db():
    from db_schema import init_database
    with app.app_context():
        db = get_db()
        init_database(db)
        print("数据库初始化完成")

# 添加自定义模板过滤器
@app.template_filter('datetime_format')
def datetime_format(value, format='%Y-%m-%d %H:%M:%S'):
    """安全的日期时间格式化过滤器"""
    if not value:
        return '未知时间'
    
    try:
        # 如果是字符串，尝试解析为datetime对象
        if isinstance(value, str):
            # 尝试多种日期格式
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format)
                except ValueError:
                    continue
            # 如果都失败了，返回原始字符串
            return value
        
        # 如果已经是datetime对象，直接格式化
        elif hasattr(value, 'strftime'):
            return value.strftime(format)
        
        # 其他情况返回字符串表示
        else:
            return str(value)
            
    except Exception as e:
        print(f"日期格式化错误: {e}, 值: {value}")
        return str(value) if value else '未知时间'

# 自定义登录验证装饰器
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 获取当前用户
def get_current_user():
    if 'user_id' in session:
        from db_utils import get_user_by_id
        return get_user_by_id(session['user_id'])
    return None

# 添加全局上下文处理器，使模板可以访问current_user
@app.context_processor
def inject_user():
    return {'current_user': get_current_user()}

# 导入并注册蓝图
try:
    from modules.system import system_bp
    from modules.auth import auth_bp
    app.register_blueprint(system_bp, name='system_bp')
    app.register_blueprint(auth_bp, name='auth')
except ImportError as e:
    print(f"错误: 导入模块失败: {e}")
    sys.exit(1)

@app.route('/')
def index():
    # 检查用户是否已登录，如果未登录则重定向到登录页面
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html')  # 确保主页显示多模态交互系统功能

# 添加一个命令行初始化数据库的命令
@app.cli.command('init-db')
def init_db_command():
    init_db()
    click.echo('数据库已初始化')

if __name__ == '__main__':
    # 检查数据库是否存在，如果不存在则初始化
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    
    app.run(debug=True)