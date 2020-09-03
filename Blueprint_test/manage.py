from flask import Flask
from admin import admin
from user import user

app = Flask(__name__)

app.register_blueprint(admin)
app.register_blueprint(user)


@app.route('/')
def index():
    return 'index'


@app.route('/list')
def ist():
    return 'list'


if __name__ == '__main__':
    print(app.url_map)
    app.run()
