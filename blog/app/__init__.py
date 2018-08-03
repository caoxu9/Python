from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
# 创建flask_login对象
login_manager = LoginManager()
# 标记登录状态复杂性
login_manager.session_protection = 'strong'
# 未登录时重定向页面
login_manager.login_view = 'auth.login'

from app.models import AnonymousUser

login_manager.anonymous_user = AnonymousUser


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 主蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 用户认证蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 管理员蓝本
    from .manager import manager as manager_blueprint
    app.register_blueprint(manager_blueprint, url_prefix='/manager')
    return app
