DB_USERNAME = 'root'
DB_PASSWORD = '123456'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'pythonbbs'

DB_URL='mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4'%(DB_USERNAME,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False


# MAIL_USE_TLS：端口号587
# MAIL_USE_SSL：端口号465
# QQ邮箱不支持非加密方式发送邮件
# 发送者邮箱的服务器地址
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
# MAIL_USE_SSL = True
MAIL_USERNAME = "1139721808@qq.com"
MAIL_PASSWORD = "wvmefqbmpffdhjhe"
MAIL_DEFAULT_SENDER = "1139721808@qq.com"

# Celery的redis配置
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

# Flask-Caching的配置
CACHE_TYPE = "RedisCache"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_HOST = "127.0.0.1"
CACHE_PORT = 6379
CACHE_DB = 0 # 通常用于指定缓存数据库的编号

SECRET_KEY = 'HVUUYFGYUFGYUDSF'

import os

# 项目根路径
BASE_DIR = os.path.dirname(__file__) # 获取当前文件所在的文件夹

from datetime import timedelta
# session.permanent=True的过期时间设置
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# 头像配置
AVATARS_SAVE_PATH = os.path.join(BASE_DIR,"media",'avatars')

# 帖子图片存放路径
POST_IMAGE_SAVE_PATH = os.path.join(BASE_DIR,"media",'post')

# 每页展示帖子的数量
PER_PAGE_COUNT = 10

# 设置JWT过期时间
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=100)

# 轮播图图片存放位置
BANNER_IMAGE_SAVE_PATH = os.path.join(BASE_DIR,"media",'banner')