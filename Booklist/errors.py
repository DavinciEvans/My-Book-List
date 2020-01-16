from Booklist import app
from flask import render_template

@app.errorhandler(404)
def page_not_found(e):  # 接受异常对象来作为参数
    return render_template("errors/404.html"), 404




@app.errorhandler(400)
def page_not_found(e):  # 接受异常对象来作为参数
    return render_template("errors/400.html"), 400



@app.errorhandler(500)
def page_not_found(e):  # 接受异常对象来作为参数
    return render_template("errors/500.html"), 500