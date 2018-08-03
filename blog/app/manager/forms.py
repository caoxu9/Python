from flask_wtf import FlaskForm
from wtforms.fields import SubmitField,SelectField,StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from app.models import Role,User

class UserForm(FlaskForm):
    email = StringField(label='邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    name = StringField(label='姓名', validators=[DataRequired(), Length(1, 32)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 64)])
    password_again = PasswordField(label='确认密码',
                                   validators=[DataRequired(), Length(1, 64), EqualTo('password', message='密码不正确')])
    location = StringField(label='位置')
    about_me = StringField(label='描述')
    confirmed = BooleanField(label='邮箱认证')
    role_id = SelectField(label='角色',coerce=int)
    submit = SubmitField(label='添加用户')

    def __init__(self):
        super(UserForm,self).__init__()
        self.role_id.choices = [(role.id, role.name) for role in (Role.query.order_by(Role.id).all())]
    def validate_name(self,field):
        user = User.query.filter_by(name=field.data).first()
        if user is not None:
            raise ValidationError('用户名存在')
    def validate_email(self,field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError('邮箱已经存在')

