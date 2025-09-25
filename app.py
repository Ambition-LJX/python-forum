from flask import Flask
from flask_migrate import Migrate
import subprocess
import time
import os
import sys
import signal

import commands
import config
from apps.cmsapi import cmsapi_bp
from apps.front import front_bp
from apps.media import media_bp
from bbs_celery import make_celery

from exts import db, mail, cache, csrf, avatars, jwt, cors

app = Flask(__name__)
app.config.from_object(config)

# 初始化扩展
db.init_app(app)
mail.init_app(app)
cache.init_app(app)
csrf.init_app(app)
avatars.init_app(app)
jwt.init_app(app)

# 正确配置 CORS（在注册蓝图前）
cors.init_app(
    app,
    resources={
        r"/cmsapi/.*": {  # 匹配所有以 /cmsapi 开头的路径
            "origins": "http://127.0.0.1:8080",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Content-Disposition"],
            "expose_headers": ["Content-Disposition"],
            "supports_credentials": True  # 允许凭据
        }
    }
)

# 排除 CSRF 验证
csrf.exempt(cmsapi_bp)
migrate = Migrate(app, db)
# 初始化 Celery
mycelery = make_celery(app)

# 注册蓝图
app.register_blueprint(front_bp)
app.register_blueprint(media_bp)
app.register_blueprint(cmsapi_bp)

# 注册命令
app.cli.command("init_boards")(commands.init_boards)
app.cli.command("init_roles")(commands.init_roles)
app.cli.command("init_developor")(commands.init_developor)

def run_app():
    print("正在启动Python论坛系统...")
    
    # 启动Celery工作进程
    celery_cmd = "celery -A app.mycelery worker --loglevel=info -P gevent"
    if os.name == 'nt':  # Windows系统
        # 使用subprocess.Popen启动Celery，并设置参数使其不弹出cmd窗口
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        celery_process = subprocess.Popen(celery_cmd, shell=True, startupinfo=startupinfo)
    else:  # Linux/Mac系统
        celery_process = subprocess.Popen(celery_cmd.split(), stdout=subprocess.PIPE)
    
    print("Celery工作进程已启动")
    
    # 等待Celery启动
    time.sleep(2)
    
    # 启动Flask应用
    print("Flask应用已启动")
    
    # 注册信号处理，确保在关闭时能够正确终止所有进程
    def signal_handler(sig, frame):
        print("正在关闭系统...")
        # 在所有系统上终止Celery进程
        celery_process.terminate()
        print("系统已关闭。")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 直接运行Flask应用，而不是通过subprocess
        app.run(host="0.0.0.0", debug=True, port=8200)  # 开发环境，开启调试模式
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)


if __name__ == '__main__':
    run_app()  # 使用run_app函数启动应用