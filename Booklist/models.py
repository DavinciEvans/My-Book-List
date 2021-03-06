from Booklist import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

# 数据库模型
class User(db.Model, UserMixin):
    # UserMixin用来增加几个属性和方法，最常用is_authenticated 属性：如果当前用户已经登录，那么
    # current_user.is_authenticated 会返回 True， 否则返回 False。
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    author = db.Column(db.String(60))

