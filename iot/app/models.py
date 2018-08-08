from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), nullable=False, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    register_time = db.Column(db.DateTime(), default=datetime.utcnow)
    access_time = db.Column(db.DateTime(), default=datetime.utcnow)
    api_key = db.Column(db.String(128))
    devices = db.relationship('Device', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    warings = db.relationship('Waring', backref='user', lazy='dynamic', cascade='all, delete-orphan')

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

    def generate_api(self):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], 60 * 60 * 24 * 365 * 10)
        self.api_key = s.dumps({'id': self.id})
        db.session.add(self)
        db.session.commit()

    def check_api(self, api_key):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(api_key)
        except:
            return False
        if data is None:
            return False
        id = data.get('id', None)
        if id is None:
            return False
        user = User.query.filter_by(id=id).first()
        if user is None:
            return False
        return True

    @staticmethod
    def check_api_key(api_key):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(api_key)
        except:
            return False
        if data is None:
            return False
        id = data.get('id', None)
        if id is None:
            return False
        user = User.query.filter_by(id=id).first()
        if user is None:
            return False
        return user


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


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    about = db.Column(db.Text)
    location = db.Column(db.String(32))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sensors = db.relationship('Sensor', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    warings = db.relationship('Waring', backref='device', lazy='dynamic', cascade='all, delete-orphan')

    def to_json(self):
        t_json = {
            'name': self.name,
            'about': self.about,
            'location': self.location,
            'time': self.time,
        }
        return t_json


class Sensor(db.Model):
    __tablename__ = 'sensor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    type = db.Column(db.Integer, db.ForeignKey('stypes.id'))
    about = db.Column(db.Text)
    unit = db.Column(db.String(16))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    datas = db.relationship('Data', lazy='dynamic', backref='sensor', cascade='all,delete-orphan')
    max = db.Column(db.Float, default=1.0)
    min = db.Column(db.Float, default=1.0)
    warings = db.relationship('Waring', backref='sensor', lazy='dynamic', cascade='all, delete-orphan')

    def to_json(self):
        t_json = {
            'name': self.name,
            'about': self.about,
            'unit': self.unit,
            'time': self.time,
            'type': self.s_type.name,
        }
        return t_json


class Stype(db.Model):
    __tablename__ = 'stypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    sensors = db.relationship('Sensor', backref='s_type', lazy='dynamic')

    @staticmethod
    def create_type():
        types = {'switch': False, 'data': True, 'gps': False}
        for type in types:
            device_type = Stype.query.filter_by(name=type).first()
            if device_type is None:
                d = Stype()
                d.name = type
                db.session.add(d)
        db.session.commit()


class Data(db.Model):
    __tablename__ = 'datas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Float)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))

    def to_json(self):
        t_json = {
            'data': self.data,
            'time': self.time,
        }
        return t_json


class Waring(db.Model):
    __tablename__ = 'warings'
    id = db.Column(db.Integer, primary_key=True)
    max = db.Column(db.Float)
    min = db.Column(db.Float)
    data = db.Column(db.Float)
    about = db.Column(db.String(32))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
