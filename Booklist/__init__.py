import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 初始化各个对象
app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# 设置各类对象的相关属性
WIN = sys.platform.startswith('win')  # 检测是否为windows
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控，提高性能，官方推荐关闭
app.config['SECRET_KEY'] = 'dev'


@app.context_processor  # 该函数可以用于设置一个全局变量，里面的东西会在任意模板中生效
def inject_user():  # 函数名可以随意修改
    from Booklist.models import User
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}


@login_manager.user_loader  # loginManager需要一个这个实例化方法
def load_user(user_id):  # 用户加载回调函数
    from Booklist.models import User
    user = User.query.get(int(user_id))
    return user

from Booklist import views, commands, errors


'''
Flask-Login 提供了一个 current_user 变量，
注册这个函数的目的是，当程序运行后，如果用户已登录， current_user 变量的值会是当前用户的用户模型类记录。
'''