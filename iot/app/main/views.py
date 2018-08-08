from app.auth.forms import LoginForm
from flask_login import login_user, logout_user, current_user
from flask import render_template, session, abort, redirect, url_for, request, flash
from . import main
from app.models import User, db, Device, Sensor,Data,Waring
from .forms import EditUserinfo, EditAdminForm, AddDevice, AddSensor
from flask_login import login_required, current_user
from app.decorators import admin_decorator, permission_decorator
from app.decorators import Permission


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (user is not None and user.check_password(form.password.data)):
            login_user(user, False)
            session['name'] = user.name
            return redirect(url_for('main.index'))
        else:
            flash('name or password is worry')
    return render_template('main/index.html', form=form)


@main.route('/user/<path:name>')
@login_required
def user_info(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        abort(404)
    return render_template('main/user_info.html', user=user)


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
    return render_template('main/edit_user.html', form=form)


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


@main.route('/devices')
@login_required
def devices():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.devices.order_by(Device.time.desc()).paginate(page, 3, False)
    ds = pagination.items
    return render_template('main/devices.html', ds=ds, pagination=pagination)


@main.route('/add_device', methods=['GET', 'POST'])
@login_required
def add_device():
    form = AddDevice()
    if form.validate_on_submit():
        device = Device()
        device.name = form.name.data
        device.about = form.about.data
        device.location = form.location.data
        device.user_id = current_user.id
        db.session.add(device)
        db.session.commit()
        return redirect(url_for('main.devices'))
    return render_template('main/add_device.html', form=form)


@main.route('/device_info')
@login_required
def device_info():
    did = request.args.get('did')
    page = request.args.get('page',1,type=int)
    if did is None:
        abort(404)
    d = current_user.devices.filter_by(id=did).first()
    pagination = d.sensors.order_by(Sensor.time.desc()).paginate(page,2,False)
    sensors = pagination.items
    return render_template('main/device_info.html', d=d, sensors=sensors,pagination=pagination)


@main.route('/add_sensor', methods=['GET', 'POST'])
@login_required
def add_sensor():
    form = AddSensor()
    did = request.args.get('did')
    if did is None:
        abort(404)
    device = current_user.devices.filter_by(id=did).first()
    if device is None:
        abort(404)
    if form.validate_on_submit():
        sensor = Sensor()
        sensor.type = form.type.data
        sensor.name = form.name.data
        sensor.about = form.about.data
        sensor.unit = form.unit.data
        sensor.max = form.max.data
        sensor.min = form.min.data
        sensor.device_id = did
        db.session.add(sensor)
        db.session.commit()
        return redirect(url_for('main.device_info', did=did))
    return render_template('main/add_sensor.html', form=form)


@main.route('/delete_device')
@login_required
def delete_device():
    did = request.args.get('did')
    if did is None:
        abort(404)
    device = current_user.devices.filter_by(id=did).first()
    if device is None:
        abort(404)
    db.session.delete(device)
    db.session.commit()
    return redirect(url_for('main.devices'))


@main.route('/edit_device', methods=['GET', 'POST'])
@login_required
def edit_device():
    did = request.args.get('did')
    if did is None:
        abort(404)
    device = current_user.devices.filter_by(id=did).first()
    if device is None:
        abort(404)
    form = AddDevice()
    if form.validate_on_submit():
        device.name = form.name.data
        device.about = form.about.data
        device.location = form.location.data
        db.session.add(device)
        db.session.commit()
        return redirect(url_for('main.devices'))
    form.name.data = device.name
    form.about.data = device.about
    form.location.data = device.location
    return render_template('main/edit_device.html', form=form)


@main.route('/delete_sensor')
@login_required
def delete_sensor():
    sid = request.args.get('sid')
    did = request.args.get('did')
    if sid is None or did is None:
        abort(404)
    device = current_user.devices.filter_by(id=did).first()
    if device is None:
        abort(404)
    sensor = device.sensors.filter_by(id=sid).first()
    if sensor is None:
        abort(404)
    db.session.delete(sensor)
    db.session.commit()
    return redirect(url_for('main.device_info', did=did))


@main.route('/edit_sensor', methods=['GET', 'POST'])
@login_required
def edit_sensor():
    sid = request.args.get('sid')
    did = request.args.get('did')
    if sid is None or did is None:
        abort(404)
    device = current_user.devices.filter_by(id=did).first()
    if device is None:
        abort(404)
    sensor = device.sensors.filter_by(id=sid).first()
    if sensor is None:
        abort(404)
    form = AddSensor()
    if form.validate_on_submit():
        sensor.type = form.type.data
        sensor.name = form.name.data
        sensor.about = form.about.data
        sensor.unit = form.unit.data
        sensor.max = form.max.data
        sensor.min = form.min.data
        db.session.add(sensor)
        db.session.commit()
        return redirect(url_for('main.device_info', did=did))
    form.name.data = sensor.name
    form.unit.data = sensor.unit
    form.about.data = sensor.about
    form.type.data = sensor.type
    form.max.data = sensor.max
    form.min.data = sensor.min
    return render_template('main/edit_sensor.html', form=form)

@main.route('/sensor_datas')
@login_required
def sensor_datas():
    page = request.args.get('page',1,type=int)
    did = request.args.get('did')
    sid = request.args.get('sid')
    if sid is None or did is None:
        abort(404)
    else:
        d = current_user.devices.filter_by(id=did).first()
        sensor = d.sensors.filter_by(id=sid).first()
        if sensor is None or d is None:
            abort(404)
        else:
            pagination = sensor.datas.paginate(page,30,False)
            datas = pagination.items
            return render_template('main/datas.html',pagination=pagination,datas=datas,sid=sid,did=did)


@main.route('/waring')
@login_required
def waring():
    page =request.args.get('page',1,type=int)
    pagination = current_user.warings.paginate(page,30,False)
    warings = pagination.items
    return render_template('main/waring.html',pagination=pagination,warings=warings)