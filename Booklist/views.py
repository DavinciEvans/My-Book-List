from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from Booklist import app, db
from Booklist.models import Book, User

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
def page_not_found(e):  # 接受异常对象来作为参数
    return render_template("errors/404.html"), 404


@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        if not title or not author or len(title) > 60 or len(author) > 60:
            flash('数值不合法！')
            return redirect(url_for('bo/ok_edit'))
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