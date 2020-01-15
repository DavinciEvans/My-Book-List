from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

app = Flask(__name__)
WIN = sys.platform.startswith('win')  # 检测是否为windows
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控，提高性能，官方推荐关闭
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dev'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    author = db.Column(db.String(60))

@app.cli.command()
def forge():
    db.create_all()
    name = "Davinci"
    BookList = [
        {'title': '人类群星闪耀时', 'author': "斯蒂芬·茨威格"},
        {'title': '高堡奇人', 'author': '菲利普·迪克'},
        {'title': '算法图解', 'author': 'UnKnown'},
        {'title': '白夜行', 'author': '东野圭吾'},
        {'title': '三体I', 'author': '刘慈欣'},
        {'title': '苏菲的世界', 'author': '乔斯坦·贾德'},
        {'title': '上帝掷骰子吗？', 'author': '曹天元'}
    ]
    user = User(name=name)
    db.session.add(user)
    for b in BookList:
        book = Book(title=b['title'], author=b['author'])
        db.session.add(book)

    db.session.commit()
    click.echo('done')

@app.cli.command()
@click.option('--drop', is_flag=True, help="Create after drop")
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initial database successful!")

# 该函数可以用于设置一个全局变量，里面的东西会在任意模板中生效
@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}

@app.route('/', methods=['GET', 'POST'])
def index():
    BookList = Book.query.all()
    if request.method == 'POST':
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
    return render_template("index.html", BookList=BookList)

@app.errorhandler(404)
def page_not_found(e): # 接受异常对象来作为参数
    return render_template("404.html"), 404

@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
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
def book_delete(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('已从列表中删除《%s》' % Book.title)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
