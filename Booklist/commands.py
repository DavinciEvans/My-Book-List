from Booklist import app, db
from Booklist.models import User, Book
import click

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