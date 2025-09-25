import random

from exts import db
from models.auth import UserModel,RoleModel,Permission
from models.post import BoardModel, PostModel

def init_boards():
    board_names = ['Python', 'Flask', 'Django', '爬虫', '前端']
    for index, board_name in enumerate(board_names):
        board = BoardModel(name=board_name, priority=len(board_names) - index)
        db.session.add(board)
    db.session.commit()
    print("版块初始化成功！")

def create_test_posts():
    boards = list(BoardModel.query.all())
    board_count = len(boards)
    for x in range(99):
        title = "我是标题%d" % x
        content = "我是内容%d" % x
        author = UserModel.query.first()
        index = random.randint(0, board_count - 1)
        board = boards[index]
        post_model = PostModel(title=title, content=content, author=author,board=board)
        db.session.add(post_model)
    db.session.commit()
    print("测试帖子添加成功！")

def init_roles():
    # 运营
    operator_role = RoleModel(name="运营", desc="负责管理帖子和评论",
                         permissions=Permission.POST | Permission.COMMENT | Permission.USER)
    # 管理员
    admin_role = RoleModel(name="管理员", desc="负责整个网站的管理",
                      permissions=Permission.POST | Permission.COMMENT | Permission.USER | Permission.STAFF)
    # 开发者（权限是最大的）
    developer_role = RoleModel(name="开发者", desc="负责网站的开发", permissions=Permission.ALL_PERMISSION)

    db.session.add_all([operator_role, admin_role, developer_role])
    db.session.commit()
    print("角色添加成功！")

# 初始化开发者
def init_developor():
    role = RoleModel.query.filter_by(name="开发者").first()
    user = UserModel(username="admin", email="19833722688@163.com", password='123456', is_staff=True, role=role)
    db.session.add(user)
    db.session.commit()
    print('开发者角色下的用户创建成功！')

def bind_roles():
    user1 = UserModel.query.filter_by(email="1139721808@qq.com").first()
    user2 = UserModel.query.filter_by(email="19833722688@163.com").first()
    user3 = UserModel.query.filter_by(email="3928436977@qq.com").first()

    role1 = RoleModel.query.filter_by(name="开发者").first()
    role2 = RoleModel.query.filter_by(name="运营").first()
    role3 = RoleModel.query.filter_by(name="管理员").first()

    user2.role = role1
    user1.role = role2
    user3.role = role3

    db.session.commit()
    print("用户和角色绑定成功！")