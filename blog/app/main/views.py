from flask import render_template, session, abort, redirect, url_for, request
from . import main
from app.models import User, db, Blog, Follow, Comment
from .forms import EditUserinfo, EditAdminForm, BlogForm, CommentForm
from flask_login import login_required, current_user
from app.decorators import admin_decorator, permission_decorator
from app.decorators import Permission


@main.route('/', methods=['GET', 'POST'])
def index():
    # blogs = Blog.query.order_by(Blog.time.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(Blog.time.desc()).paginate(page, 5, False)
    blogs = pagination.items
    return render_template('main/index.html', pagination=pagination, blogs=blogs)


@main.route('/write_blog', methods=['GET', 'POST'])
@login_required
@permission_decorator(Permission.WRITE)
def write_blog():
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog()
        blog.title = form.title.data
        blog.body = form.body.data.replace("\n", "<br>")
        blog.author_id = current_user.id
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('main/write_blog.html', form=form)


@main.route('/user/<path:name>')
@login_required
def user_info(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        abort(404)
    # blogs = Blog.query.filter_by(author=user).order_by(Blog.time.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = user.blogs.order_by(Blog.time.desc()).paginate(page, 5, False)
    blogs = pagination.items
    return render_template('main/user_info.html', user=user, blogs=blogs, pagination=pagination)


@main.route('/edit_user_info', methods=['GET', 'POST'])
@login_required
def edit_user_info():
    form = EditUserinfo()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.user_info', name=current_user.name))
    return render_template('main/edit_user_info.html', form=form)


@main.route('/edit_admin', methods=['GET', 'POST'])
@login_required
@admin_decorator
def edit_admin():
    id = request.args.get('id', None)
    if id is None:
        abort(404)
    user = User.query.filter_by(id=id).first()
    form = EditAdminForm()
    if form.validate_on_submit():
        u1 = User.query.filter_by(name=form.name.data).first()
        if u1 is None:
            abort(404)
        if u1 and u1 != user:
            return redirect(url_for('main.user_info', name=user.name))
        user.name = form.name.data
        if form.password.data:
            user.password = form.password.data
        user.about_me = form.about_me.data
        user.location = form.location.data
        user.role_id = form.role_id.data
        user.confirmed = form.comfirmed.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.user_info', name=user.name))
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.comfirmed.data = user.confirmed
    form.role_id.data = user.role_id
    return render_template('main/edit_admin.html', form=form)


@main.route('/blog/<id>', methods=['GET', 'POST'])
@login_required
def blog(id):
    if id is None:
        abort(404)
    blog = Blog.query.filter_by(id=int(id)).first()
    if blog is None:
        abort(404)
    form = CommentForm()
    if current_user.has_permission(Permission.COMMENT):
        if form.validate_on_submit():
            comment = Comment()
            comment.blog_id = blog.id
            comment.author_id = current_user.id
            comment.body = form.comment.data
            comment.disabled = False
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('main.blog', id=blog.id))
    # comments = Comment.query.filter_by(blog_id = blog.id).all()
    page = request.args.get('page', type=int, default=1)
    pagination = blog.comments.order_by(Comment.time.desc()).paginate(page, 3, False)
    comments = pagination.items
    return render_template('main/blog.html', blog=blog, form=form, comments=comments, pagination=pagination)


@main.route('/blog_delete')
@login_required
def blog_delete():
    blog_id = request.args.get('blog_id')
    if blog_id is None:
        abort(404)
    blog = current_user.blogs.filter_by(id=blog_id).first()
    if blog is None:
        abort(404)
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('main.user_info', name=current_user.name))


@main.route('/follow')
@permission_decorator(Permission.FOLLOW)
def follow():
    uid = request.args.get('uid')
    if uid is None:
        abort(404)
    user = User.query.filter_by(id=uid).first()
    if user is None:
        abort(404)
    current_user.follow(user)
    return redirect(url_for('main.user_info', name=user.name))


@main.route('/unfollow')
@permission_decorator(Permission.FOLLOW)
def unfollow():
    uid = request.args.get('uid')
    if uid is None:
        abort(404)
    user = User.query.filter_by(id=uid).first()
    if user is None:
        abort(404)
    current_user.unfollow(user)
    return redirect(url_for('main.user_info', name=user.name))


@main.route('/fans')
@login_required
def fans():
    uid = request.args.get('uid')
    if uid is None:
        abort(404)
    user = User.query.filter_by(id=uid).first()
    fans = user.followers.order_by(Follow.time.desc()).all()
    fans_list = []
    for fan in fans:
        fans_list.append(fan.follower)
    return render_template('main/fans.html', fans_list=fans_list)
