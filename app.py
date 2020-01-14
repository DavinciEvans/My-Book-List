from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

app = Flask(__name__)
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app)

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    author = db.Column(db.String(60))

@app.route('/', methods=['GET'])
def index():
    name = User.query.first().name
    BookList = Book.query.all()
    return render_template("index.html", BookList=BookList, name=name)


if __name__ == '__main__':
    app.run()
