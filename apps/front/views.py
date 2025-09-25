import os
import random
import string
import time
from hashlib import md5
from io import BytesIO

from exts import cache, db
from flask import Blueprint, request, render_template, current_app, make_response, session, redirect, g, jsonify, \
    url_for
from flask_avatars import Identicon
from flask_jwt_extended import create_access_token
from flask_paginate import get_page_parameter, Pagination
from models.auth import UserModel, Permission
from models.post import BoardModel, PostModel, CommentModel, BannerModel
from sqlalchemy.sql import func
from utils import restful
from utils.captcha import Captcha

from .decorators import login_required
from .forms import RegisterForm, LoginForm, UploadImageForm, EditProfileForm, PublicPostForm, PublicCommentForm

bp = Blueprint('front', __name__, url_prefix='/')


# 钩子函数:before_request
@bp.before_request
def front_before_request():
    if 'user_id' in session:
        user_id = session.get('user_id')
        user = UserModel.query.get(user_id)
        # 确保user存在
        if user:
            setattr(g, "user", user)  # 给user设置一个全局的属性


# 请求 => before_request => 视图函数(返回模版) => context_processor => 将context_processor返回的变量也添加到模版中

# 上下文处理器
@bp.context_processor
def front_context_processor():
    if hasattr(g, 'user'):
        return {"user": g.user}
    else:
        return {}


@bp.route('/')
def index():  # put application's code here
    sort = request.args.get('sort', type=int, default=1)
    board_id = request.args.get('board_id', type=int, default=None)
    boards = BoardModel.query.order_by(BoardModel.priority.desc()).all()
    post_query = None
    if sort == 1:
        post_query = PostModel.query.order_by(PostModel.created_time.desc())
    else:
        # 根据评论数量进行排序
        post_query = db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id).order_by(
            func.count(CommentModel.id).desc(), PostModel.created_time.desc())

    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * current_app.config['PER_PAGE_COUNT']  # 每页的起始值
    end = start + current_app.config['PER_PAGE_COUNT']  # 每页的结束值

    # 如果前端页面点击了板块的选项 则显示id对应的评论内容
    if board_id:
        post_query = post_query.filter(PostModel.board_id == board_id)
    total = post_query.count()  # 帖子的总数量
    posts = post_query.slice(start, end)
    pagination = Pagination(bs_version=3, page=page, total=total, prev_label="上一页", next_label="下一页")

    banners = BannerModel.query.order_by(BannerModel.priority.desc()).all()
    context = {'boards': boards, 'posts': posts, 'pagination': pagination, "sort": sort, "board_id": board_id,
               "banners": banners}

    return render_template("front/index.html", **context)


@bp.get('/email/captcha/')
def email_captcha():
    # 通过url后缀 ?email=xx@qq.com
    email = request.args.get('email')
    if not email:
        return restful.params_error(message="请先输入邮箱！")
    # 随机的六位数字
    source = list(string.digits)
    captcha = "".join(random.sample(source, 6))
    subject = "【Python论坛】注册验证码"
    body = "【Python论坛】您的注册验证码为:%s，验证码有效期为5分钟，请勿泄露给他人。" % captcha
    
    # 尝试发送邮件，但不影响验证码生成和返回
    try:
        current_app.celery.send_task("send_mail", (email, subject, body))
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
    
    # 对邮箱地址进行md5编码作为缓存键，避免特殊字符问题
    cache_key = md5(email.encode('utf-8')).hexdigest()
    cache.set(cache_key, captcha, timeout=300)  # 设置缓存，5分钟有效期
    print(f"验证码已缓存: {cache_key} -> {captcha}")
    
    # 不再返回验证码，只返回成功消息
    return restful.ok(message="验证码已发送到您的邮箱")


@bp.route('/graph/captcha/')
def graph_captcha():
    # 调用验证码生成类 生成验证码和图片
    captcha, image = Captcha.gene_graph_captcha()
    # 将验证码和对应的key值 设置到缓存中
    key = md5((captcha + str(time.time())).encode('utf-8')).hexdigest()  # 得到md5加密之后的md5字符串
    cache.set(key, captcha)
    # 将数据保存到内存中
    out = BytesIO()
    image.save(out, 'png')
    # 把out的文件指针指向最开始的位置
    out.seek(0)
    resp = make_response(out.read())
    resp.content_type = "image/png"
    resp.set_cookie('_graph_captcha_key', key, max_age=3600)
    return resp


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("front/login.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember_me = form.remember_me.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                return restful.params_error("邮箱或者密码错误！")
            if not user.check_password(password):
                return restful.params_error("邮箱或者密码错误！")
            session["user_id"] = user.id
            token = ""  # 如果是员工,才生成token
            permissions = []
            if user.is_staff:
                token = create_access_token(identity=user.id)  # 生成含有标识符的token
                for attr in dir(Permission):
                    if not attr.startswith("_"):
                        permission = getattr(Permission, attr)
                        if user.has_permission(permission):
                            permissions.append(attr.lower())
            if remember_me == 1:
                # 默认session过期时间 只要浏览器关闭了就会过期
                session.permanent = True
            user_dict = user.to_dict()
            user_dict['permissions'] = permissions
            return restful.ok(data={"token": token, "user": user_dict})
        else:
            return restful.params_error(message=form.message[0])


@bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("front/register.html")
    else:
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            identicon = Identicon()
            filenames = identicon.generate(text=md5(email.encode('utf-8')).hexdigest())
            avatar = filenames[2]
            # 创建用户时不要手动设置ID，让数据库自动生成
            user = UserModel(email=email, username=username, password=password, avatar=avatar)
            try:
                db.session.add(user)
                db.session.commit()
                return restful.ok()
            except Exception as e:
                db.session.rollback()
                print(f"数据库错误: {e}")
                return restful.params_error(message="注册失败，请稍后再试")
        else:
            message = form.message[0]
            return restful.params_error(message=message)


# 退出登录
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect('/')


@bp.route('/setting/')
@login_required  # 把setting路由函数当做参数带入到装饰器函数中
def setting():
    email_hash = md5(g.user.email.encode('utf-8')).hexdigest()
    # 明确传递user参数给模板
    return render_template("front/setting.html", user=g.user, email_hash=email_hash)


@bp.post('/avatar/upload/')
@login_required
def upload_avatar():
    form = UploadImageForm(request.files)
    if form.validate():
        image = form.image.data
        # 不要使用用户上传上来的文件名 否则容易被黑客攻击
        filename = image.filename
        # xxx.png,xx.jpeg
        _, ext = os.path.splitext(filename)
        filename = md5((g.user.email + str(time.time())).encode('utf-8')).hexdigest() + ext
        image_path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)
        image.save(image_path)
        # 看个人需求 是否图片上传完成后要立马修改用户的头像字段
        g.user.avatar = filename
        db.session.commit()
        return restful.ok(data={"avatar": filename})
    else:
        message = form.message[0]
        return restful.params_error(message=message)


@bp.post('/profile/edit/')
@login_required
def edit_profile():
    form = EditProfileForm(request.form)
    if form.validate():
        signature = form.signature.data
        g.user.signature = signature
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(message=form.message[0])


@bp.route('/post/public/', methods=['GET', 'POST'])
@login_required
def public_post():
    if request.method == 'GET':
        boards = BoardModel.query.order_by(BoardModel.priority.desc()).all()
        return render_template("front/public_post.html", boards=boards)
    else:
        form = PublicPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            try:
                # get方法:接受一个id作为参数 如果找到了 那么会返回这条数据
                # 如果没有找到 那么会抛出异常
                board = BoardModel.query.get(board_id)
            except Exception as e:
                return restful.params_error(message="板块不存在！")
            post_model = PostModel(title=title, content=content, board=board, author=g.user)
            db.session.add(post_model)
            db.session.commit()
            return restful.ok(data={"id": post_model.id})
        else:
            return restful.params_error(message=form.message[0])  # 参数错误


@bp.post("/post/image/upload")
@login_required
def upload_post_image():
    form = UploadImageForm(request.files)
    if form.validate():
        image = form.image.data
        # 不要使用用户上传上来的文件名，否则容易被黑客攻击
        filename = image.filename
        # xxx.png,xx.jpeg
        _, ext = os.path.splitext(filename)
        filename = md5((g.user.email + str(time.time())).encode("utf-8")).hexdigest() + ext
        image_path = os.path.join(current_app.config['POST_IMAGE_SAVE_PATH'], filename)
        image.save(image_path)
        # {"data","code", "message"}
        return jsonify({"errno": 0, "data": [
            {"url": url_for("media.get_post_image", filename=filename), "alt": filename, "href": ""}]})
    else:
        message = form.message[0]
        return restful.params_error(message=message)

# 帖子详情页
@bp.get("/post/detail/<post_id>")
def post_detail(post_id):
    post_model = PostModel.query.get(post_id)
    comment_count = CommentModel.query.filter_by(post_id=post_id).count()
    context = {
        "comment_count": comment_count,
        "post": post_model
    }
    return render_template("front/post_detail.html", **context) # 等价于下行代码  # return render_template("front/", post=post_model,comment_count=comment_count)

@bp.post("/comment")
@login_required
def public_comment():
    form = PublicCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        try:
            post_model = PostModel.query.get(post_id)
        except Exception as e:
            return restful.params_error(message="帖子不存在！")
        comment = CommentModel(content=content, post_id=post_id, author_id=g.user.id)
        db.session.add(comment)
        db.session.commit()
        return restful.ok()
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


@bp.get('/cms')
def cms():
    return render_template("cms/index.html")
