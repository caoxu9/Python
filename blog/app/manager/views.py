from . import manager
from flask import render_template, url_for, redirect, request, abort
from app.decorators import permission_decorator, admin_decorator, assient_decorator
from app.models import Permission, User, Blog,Comment
from app import db
from flask_login import login_required
from .forms import UserForm


@manager.route('/manager_user')
@login_required
@admin_decorator
def manager_user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.register_time.desc()).paginate(page, 10, False)
    users = pagination.items
    return render_template('manager/manager_user.html', users=users, pagination=pagination)


@manager.route('/manager_blog')
@login_required
@admin_decorator
def manager_blog():
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(Blog.time.desc()).paginate(page, 10, False)
    blogs = pagination.items
    return render_template('manager/manager_blog.html', pagination=pagination, blogs=blogs)


@manager.route('/manager_delete_user')
@login_required
@admin_decorator
def manager_delete_user():
    id = request.args.get('id')
    if id is None:
        abort(404)
    user = User.query.filter_by(id = id ).first()
    if user is None:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    page = request.args.get('page',1,type=int)
    pagination = User.query.order_by(User.register_time.desc()).paginate(page,10,False)
    users = pagination.items
    return redirect(url_for('.manager_user',pagination=pagination,users=users))



@manager.route('/manager_delete_blog')
@login_required
@admin_decorator
def manager_delete_blog():
    id = request.args.get('id')
    if id is None:
        abort(404)
    blog = Blog.query.filter_by(id=id).first()
    if blog is None:
        abort(404)
    db.session.delete(blog)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(Blog.time.desc()).paginate(page, 10, False)
    blogs = pagination.items
    return redirect(url_for('.manager_blog', pagination=pagination, blogs=blogs))


@manager.route('/decorator')
@assient_decorator
def manager_decorator():
    return render_template('manager/manager_user.html')


@manager.route('/manager_add_user',methods=['GET','POST'])
@admin_decorator
def manager_add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.password = form.password.data
        user.role_id = form.role_id.data
        user.about_me = form.about_me.data
        user.location = form.location.data
        user.confirmed = form.confirmed.data
        print(form.confirmed.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.manager_user'))
    return render_template('manager/manager_add_user.html',form=form)


@manager.route('/manager_comment')
@admin_decorator
def manager_comment():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.time.desc()).paginate(page,1,False)
    comments = pagination.items
    return render_template('manager/manager_comment.html',comments=comments,pagination=pagination)