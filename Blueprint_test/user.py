from flask import Blueprint

user = Blueprint('user', __name__)


@user.route('/user/hello')
def hello():
    return '/user/hello'


@user.route('/user/new')
def new():
    return '/user/new'


@user.route('/user/edit')
def edit():
    return '/user/edit'
