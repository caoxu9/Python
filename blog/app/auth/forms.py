from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField(label='邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(label='密码', validators=[DataRequired()])
    remember_me = BooleanField(label='记住我', default=False)
    submit = SubmitField(label='登录')


class Register(FlaskForm):
    email = StringField(label='邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    name = StringField(label='姓名', validators=[DataRequired(), Length(1, 32)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 64)])
    password_again = PasswordField(label='确认密码',
                                   validators=[DataRequired(), Length(1, 64), EqualTo('password', message='密码不正确')])
    submit = SubmitField(label='注册')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError('邮箱已经被注册')

    def validate_name(self, field):
        user = User.query.filter_by(name=field.data).first()
        if user is not None:
            raise ValidationError('姓名已经被注册')
