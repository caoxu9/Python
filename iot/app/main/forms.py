from flask_wtf import FlaskForm
from wtforms.fields import StringField,SubmitField,PasswordField,SelectField,BooleanField,FloatField
from wtforms import TextAreaField
from wtforms.validators import Length,DataRequired
from app.models import Role,Stype


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


class AddDevice(FlaskForm):
    name = StringField(label='设备名称',validators=[DataRequired()])
    about = TextAreaField(label='设备描述',validators=[DataRequired()])
    location = StringField(label='设备位置',validators=[DataRequired()])
    submit = SubmitField(label='添加设备')



class AddSensor(FlaskForm):
    name = StringField(label='传感器名称',validators=[DataRequired()])
    type = SelectField(label='传感器类型',coerce=int)
    about = TextAreaField(label='传感器描述',validators=[DataRequired()])
    unit = StringField(label='传感器单位',validators=[DataRequired()])
    max = FloatField(label='最大值')
    min = FloatField(label='最小值')
    submit = SubmitField(label='添加传感器')
    def __init__(self):
        super(AddSensor,self).__init__()
        self.type.choices = [(stype.id,stype.name) for stype in Stype.query.all()]

