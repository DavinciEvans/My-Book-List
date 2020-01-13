from flask import Flask, render_template

app = Flask(__name__)

name = "DavinciEvans"
BookList = [
    {'title': '人类群星闪耀时', 'author': "基辛格"},
    {'title': '高堡奇人', 'author':'菲利普·迪克'},
    {'title': '算法图解', 'author':'UnKnown'},
    {'title': '白夜行', 'author':'东野圭吾'},
    {'title': '三体I', 'author':'刘慈欣'},
    {'title': '苏菲的世界', 'author':'乔斯坦·贾德'},
    {'title': '上帝掷骰子吗？','author':'曹天元'}
]

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", BookList=BookList, name=name)


if __name__ == '__main__':
    app.run()
