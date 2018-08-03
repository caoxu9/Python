from flask_wtf import FlaskForm
from wtforms.fields import StringField,SubmitField,PasswordField,SelectField,BooleanField
from wtforms import TextAreaField
from wtforms.validators import Length,DataRequired,Required
from app.models import Role
from flask_pagedown.fields import PageDownField

class EditUserinfo(FlaskForm):
    location = StringField(label='所在地',validators=[Length(0,64)])
    about_me = TextAreaField(label='AboutMe')
    submit = SubmitField(label='提交')

class EditAdminForm(FlaskForm):
    name = StringField(label='姓名')
    password = PasswordField(label='密码')
    role_id = SelectField(label='角色',coerce=int)
    comfirmed = BooleanField(label='邮箱认证')
    location = StringField(label='所在地')
    about_me = TextAreaField(label='AboutMe')
    submit = SubmitField(label='提交')

    def __init__(self,*args,**kwargs):
        super(EditAdminForm, self).__init__(*args,**kwargs)
        self.role_id.choices = [(role.id,role.name) for role in (Role.query.order_by(Role.id).all())]


class BlogForm(FlaskForm):
    title = StringField(label='博客标题',validators=[DataRequired()])
    body = PageDownField(label='博客正文',validators=[DataRequired()])
    submit = SubmitField(label='提交')


class CommentForm(FlaskForm):
    comment = TextAreaField(validators=[DataRequired()])
    submit = SubmitField(label='评论')
