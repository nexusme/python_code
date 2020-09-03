from flask import Blueprint

admin = Blueprint('admin', __name__)


@admin.route('/admin/hello')
def hello():
    return '/admin/hello'


@admin.route('/admin/new')
def new():
    return '/admin/new'


@admin.route('/admin/edit')
def edit():
    return '/admin/edit'
