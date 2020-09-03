from flask import Flask, redirect, url_for
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
# 先绑定一个api，进行初始化操作
api = Api(app)


# class LoginView(Resource):
#     def get(self, username):
#         return {"simple": 'hello ,world'}
#
#
# api.add_resource(LoginView, '/<username>/', endpoint='login')
#
#
# #
# @app.route('/login1/')
# def login1():
#     return redirect(url_for('login', username='1'))
#


class LoginView(Resource):
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        # reqparse 是一个类似于WTforms验证的一个模板，用这个模板的时候，需要先进行引用，然后和WTForms的功能就差不了，就是一个验证用户输入的功能。
        username = parser.add_argument('username', type=str, help='Username is empty.', required=True)
        # 定义一个username,说明用户需要传入关于username的一个值()后面的都是参数.括号里面的参数可以先不考虑
        password = parser.add_argument('password', type=str, help='Password is empty')
        # 定义一个password,说明用户需要传入关于password的一个值()后面的都是参数.括号里面的参数可以先不考虑
        args = parser.parse_args()
        # 对用户传入的参数进行解析，不解析的话，是会报错的
        print(args)
        return args['username'] + ', you have successfully registered!'


api.add_resource(LoginView, '/')
if __name__ == '__main__':
    app.run(debug=True)
