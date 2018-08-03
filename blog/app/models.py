from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    time = db.Column(db.DateTime,default = datetime.utcnow,index=True)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),nullable=False,index=True)
    password_hash = db.Column(db.String(128),nullable=False)
    email = db.Column(db.String(64),nullable=False,index=True)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    register_time = db.Column(db.DateTime(), default=datetime.utcnow)
    access_time = db.Column(db.DateTime(), default=datetime.utcnow)
    comments = db.relationship('Comment',backref='comment_man',lazy='dynamic')
    blogs = db.relationship('Blog',backref='author',lazy='dynamic')
    followers = db.relationship('Follow', \
                                foreign_keys=[Follow.followed_id], \
                                backref=db.backref('followed', lazy='joined'), \
                                lazy='dynamic', \
                                cascade='all, delete-orphan')
    followeds = db.relationship('Follow', \
                                foreign_keys=[Follow.follower_id], \
                                backref=db.backref('follower', lazy='joined'), \
                                lazy='dynamic', \
                                cascade='all, delete-orphan')

    def follow(self, user):
        if not self.is_follower_of(user):
            f = Follow()
            f.follower = self
            f.followed = user
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        if self.is_follower_of(user):
            f = self.followeds.filter_by(followed_id=user.id).first()
            db.session.delete(f)
            db.session.commit()

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None


    def is_follower_of(self, user):
        return self.followeds.filter_by(followed_id=user.id).first() is not None
    def __str__(self):
        return '[' + self.name + ':' + str(self.id) + ']'

    @property
    def password(self):
        raise AttributeError('密码不允许读取')

    @password.setter
    def password(self, pd):
        self.password_hash = generate_password_hash(pd)

    def check_password(self, pd):
        return check_password_hash(self.password_hash, pd)

    def generate_token(self, timeout=60):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], timeout)
        token = s.dumps({'id': self.id})
        return token

    def check_token(self, token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        id = data.get('id', None)
        if id is None:
            return None

        user = User.query.filter_by(id=id).first()
        if user is None:
            return False
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return True

    def has_permission(self, permissions):
        if self.role is None:
            return False
        if self.role.permissions & permissions == permissions:
            return True
        return False

    def is_admin(self):
        return self.has_permission(Permission.ADMIN)

    def flush_access_time(self):
        self.access_time = datetime.now()
        db.session.add(self)
        db.session.commit()



    @staticmethod
    def generate_fake_user(count):
        import forgery_py
        for i in range(count):
            user = User()
            user.email = forgery_py.internet.email_address()
            user.name = forgery_py.internet.user_name()
            user.location = forgery_py.address.city()
            user.about_me = forgery_py.lorem_ipsum.title()
            user.password = forgery_py.lorem_ipsum.word()
            user.confirmed = True
            db.session.add(user)
            try:
                db.session.commit()
            except:
                db.session.rollback()

from flask_login import AnonymousUserMixin


class AnonymousUser(AnonymousUserMixin):

    name = '游客'
    def has_permission(self, permissions):
        return False

    def is_admin(self):
        return False


# 当调用logout_user时候调用，用来查询user
from . import login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=int(id)).first()


class Permission():
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE = 0x04
    MODE_COMMENT = 0x08
    ADMIN = 0xff


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    @staticmethod
    def create_roles():
        roles = {
            'user': [Permission.FOLLOW | Permission.COMMENT | Permission.WRITE, True],
            'moderator': [Permission.FOLLOW | Permission.COMMENT | Permission.WRITE | Permission.MODE_COMMENT, False],
            'admin': [Permission.ADMIN, False],
        }
        for name in roles:
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = Role()
                role.name = name
            role.permissions = roles[name][0]
            role.default = roles[name][1]
            db.session.add(role)
        db.session.commit()


class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(1024))
    body = db.Column(db.Text)
    time = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    comments = db.relationship('Comment',backref='blog',lazy='dynamic')


    @staticmethod
    def generate_fake_blog(count):
        import forgery_py
        from random import randint
        num = User.query.count()-1
        for i in range(count):
            blog = Blog()
            blog.title = forgery_py.lorem_ipsum.title()
            blog.body = forgery_py.lorem_ipsum.sentence()
            blog.author = User.query.offset(randint(1,num)).first()
            db.session.add(blog)
        try:
            db.session.commit()
        except:
            db.session.rollback()



    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'br']
        m =markdown(value,output_format='html')
        bm = bleach.clean(m,tags=allowed_tags,strip=True)
        target.body_html = bleach.linkify(bm)

db.event.listen(Blog.body,'set',Blog.on_change_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    blog_id = db.Column(db.Integer,db.ForeignKey('blogs.id'))
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    disabled = db.Column(db.Boolean)
    time = db.Column(db.DateTime,default=datetime.utcnow,index=True)


