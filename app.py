from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import sys
import click

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
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控，提高性能，官方推荐关闭
app.config['SECRET_KEY'] = 'dev'
login_manager.login_view = 'login'


@app.context_processor  # 该函数可以用于设置一个全局变量，里面的东西会在任意模板中生效
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}


@login_manager.user_loader  # loginManager需要一个这个实例化方法
def load_user(user_id):  # 用户加载回调函数
    user = User.query.get(int(user_id))
    return user


'''
Flask-Login 提供了一个 current_user 变量，
注册这个函数的目的是，当程序运行后，如果用户已登录， current_user 变量的值会是当前用户的用户模型类记录。
'''


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


# 命令行操作指令
@app.cli.command()
@click.option('--username', prompt=True, help="set Username to login")
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help="password used to login")
def admin(username, password):  # 管理员注册或修改号码
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Create user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done')


@app.cli.command()
def forge():  # 数据库数据初始化
    db.create_all()
    name = "Davinci"
    booklist = [
        {'title': '人类群星闪耀时', 'author': "斯蒂芬·茨威格"},
        {'title': '高堡奇人', 'author': '菲利普·迪克'},
        {'title': '算法图解', 'author': 'UnKnown'},
        {'title': '白夜行', 'author': '东野圭吾'},
        {'title': '三体I', 'author': '刘慈欣'},
        {'title': '苏菲的世界', 'author': '乔斯坦·贾德'},
        {'title': '上帝掷骰子吗？', 'author': '曹天元'}
    ]
    for b in booklist:
        book = Book(title=b['title'], author=b['author'])
        db.session.add(book)

    db.session.commit()
    click.echo('done')


@app.cli.command()
@click.option('--drop', is_flag=True, help="Create after drop")
def initdb(drop):  # 数据库初始化
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initial database successful!")


# 路由
@app.route('/', methods=['GET', 'POST'])
def index():
    booklist = Book.query.all()
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        author = request.form.get('author')
        if not title or not author or len(title) > 60 or len(author) > 60:
            flash('数值不合法！')
            return redirect(url_for('index'))
        book = Book(title=title, author=author)
        db.session.add(book)
        db.session.commit()
        flash('添加书籍成功！')
        return redirect(url_for('index'))
    return render_template("index.html", BookList=booklist)


@app.errorhandler(404)
def page_not_found(e): # 接受异常对象来作为参数
    return render_template("404.html"), 404


@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        if not title or not author or len(title) > 60 or len(author) > 60:
            flash('数值不合法！')
            return redirect(url_for('book_edit'))
        book.title = title
        book.author = author
        db.session.commit()
        flash('数据已更新！')
        return redirect(url_for('index'))
    return render_template('edit.html', book=book)


@app.route('/book/delete/<int:book_id>', methods=['POST'])
@login_required
def book_delete(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('已从列表中删除')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():  # 登录
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("数值不合法！")
            return redirect(url_for('login'))
        user = User.query.first()
        if user.username == username and user.validate_password(password):
            login_user(user)
            flash("登录成功")
            return redirect(url_for('index'))
        flash('登录失败，请检查账户名或密码是否正确')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required  # 用于视图保护
def logout():  # 登出
    logout_user()
    flash('GoodBye.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 60:
            flash('数值不合法！')
            return redirect('settings')

        current_user.name = name  # current_user会返回当前用户数据库记录对象
        db.session.commit()
        flash('设置成功！')
        return redirect(url_for('index'))
    return render_template('settings.html')

if __name__ == '__main__':
    app.run()
