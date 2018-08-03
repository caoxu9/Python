from . import auth
from flask import render_template, url_for, session, redirect, flash, current_app, request
from .forms import LoginForm, Register
from app.models import User
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.email import send_mail


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (user is not None and user.check_password(form.password.data)):
            login_user(user, form.remember_me.data)
            session['name'] = user.name
            return redirect(url_for('main.index'))
        else:
            flash('name or password is worry')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.errorhandler(AttributeError)
def error_handle(e):
    flash(str(e))
    return redirect(url_for('auth.register'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    from app.models import Role
    form = Register()
    if form.validate_on_submit():
        user = User()
        user.name = form.name.data
        user.password = form.password.data
        user.email = form.email.data
        if user.email == current_app.config['MAIL_USERNAME']:
            user.role = Role.query.filter_by(permissions=0xff).first()
        else:
            user.role = Role.query.filter_by(default=True).first()
        db.session.add(user)
        db.session.commit()

        token = user.generate_token()
        html = render_template('email/register.html', token=token, name=user.name)
        send_mail('博客注册验证', current_app.config['MAIL_USERNAME'], [form.email.data], None, html)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm')
@login_required
def confirm():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    token = request.args.get('token')
    status = current_user.check_token(token)
    if status:
        return redirect(url_for('main.index'))
    return render_template('email/reset_mail.html', name=current_user.name)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.flush_access_time()
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirm'))


@auth.route('/unconfirm')
@login_required
def unconfirm():
    return render_template('auth/unconfirm.html', name=current_user.name)


@auth.route('/reset_mail')
def reset_mail():
    token = current_user.generate_token()
    html = render_template('email/reset_mail.html', token=token, name=current_user.name)
    send_mail('曹旭注册验证', current_app.config['MAIL_USERNAME'], [current_user.email], None, html)
    return redirect(url_for('auth.unconfirm'))
