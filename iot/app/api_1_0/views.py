from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g,request,current_app
from app.api_1_0 import api
from app.models import User,Device,Sensor,Data,Waring
import time
from datetime import datetime
from app import db

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(api_key, password):
    if api_key == '':
        return False
    if password == '':
        print('password',password)
        g.current_user = User.check_api_key(api_key)
        if g.current_user:
            return True
    user = User.query.filter_by(email=api_key).first()
    if user is None:
        return False
    else:
        return True


@auth.error_handler
def error():
    return jsonify({'status': 401})

#获取token
@api.route('/token')
@auth.login_required
def token():
    token = g.current_user.api_key
    if token:
        return jsonify({'status': 200, 'token': token})
    else:
        return jsonify({'status': 401})


# 获取一个用户的所有设备
# url
# /api/1.0/devices
# 方法：GET
# 返回的数据类型
# 成功：{'status':200, 'devices':device_list}
# 失败：{'status':404}
@api.route('/devices')
@auth.login_required
def devices():
    d = g.current_user.devices.order_by(Device.time.desc()).all()
    if d is None:
        return jsonify({'status': 401})
    d_list = []
    for i in d:
        d_list.append(i.to_json())
    return jsonify({'status':200,'devices':d_list})


# 获取一个用户的某个设备
# url
# /api/1.0/device/<device_id>
# 方法：GET
# 返回的数据类型
# 成功：{'status':200, 'device':device}
# 失败：{'status':404}
@api.route('/device/<int:device_id>')
@auth.login_required
def device(device_id):
    d = g.current_user.devices.filter_by(id=device_id).first()
    if d is None:
        return jsonify({'status': 401})
    else:
        return jsonify({'status': 200,'device':d.to_json()})



# 获取一个设备的所有传感器
# url
# /api/1.0/device/<device_id>/sensors
# 方法：GET
# 返回的数据类型
# 成功：{'status':200, 'sensors':sensor_list}
# 失败：{'status':404}
@api.route('/device/<int:device_id>/sensors')
@auth.login_required
def sensors(device_id):
    d = g.current_user.devices.filter_by(id=device_id).first()
    if d is None:
        return jsonify({'status': 401})
    else:
        ss = d.sensors.order_by(Sensor.time.desc()).all()
        s_list = []
        for s in ss:
            s_list.append(s.to_json())
        return jsonify({'status':200,'sensors':s_list})

# 获取一个设备的某个传感器
# url
# /api/1.0/device/<device_id>/sensor/<sensor_id>
# 方法：GET
# 返回的数据类型
# 成功：{'status':200, 'sensor':sensor}
# 失败：{'status':404}
@api.route('/device/<int:device_id>/sensor/<int:sensor_id>')
@auth.login_required
def sensor(device_id,sensor_id):
    d = g.current_user.devices.filter_by(id=device_id).first()
    if d is None:
        return jsonify({'status':404})
    else:
        s = d.sensors.filter_by(id=sensor_id).first()
        return jsonify({'status':200,'sensor':s.to_json()})


# 获取一个传感器的所有数据
# url
# /api/1.0/device/<device_id>/sensor/<sensor_id>/datas
# 方法：GET
# 返回的数据类型
# 成功：{'status':200, 'datas':data_list}
# 失败：{'status':404}
@api.route('/device/<int:device_id>/sensor/<int:sensor_id>/datas')
@auth.login_required
def datas(device_id,sensor_id):
    d = g.current_user.devices.filter_by(id=device_id).first()
    if d is None:
        return jsonify({'status': 404})
    else:
        s = d.sensors.filter_by(id=sensor_id).first()
        if s is None:
            return jsonify({'status': 404})
        data = s.datas.order_by(Data.time.desc()).all()
        d_list = []
        for dd in data:
            d_list.append(dd.to_json())
        return jsonify({'status':200,'datas':d_list})


# 获取一个传感器的某页数据（每页60个数据）
# url
# /api/1.0/device/<int:device_id>/sensor/<int:sensor_id>/pdatas/<int:page>
# 方法：GET
# 返回的数据类型
# 成功：{'status':200, 'datas':data_list}
# 失败：{'status':404}
@api.route('/device/<int:device_id>/sensor/<int:sensor_id>/pdatas/<int:page>')
@auth.login_required
def pdatas(device_id,sensor_id,page):
    ds = g.current_user.devices.filter_by(id=device_id).first()
    if ds is None:
        return jsonify({'status':404})
    else:
        ss = ds.sensors.filter_by(id=sensor_id).first()
        if ss is None:
            return jsonify({'status': 404})
        else:
            pagination = ss.datas.paginate(page,60,False)
            data = pagination.items
            data_list = []
            for i in data:
                data_list.append(i.to_json())
            return jsonify({'status':200,'data':data_list})

# 获取一个传感器的最新数据
# url
# /api/1.0/device/<device_id>/sensor/<sensor_id>/data
# 方法：GET
# 返回的数据类型
# 成功：{'status':200, 'data':data}
# 失败：{'status':404}
@api.route('/device/<int:device_id>/sensor/<int:sensor_id>/data',methods=['GET','POST'])
@auth.login_required
def newdata(device_id,sensor_id):
    count = current_app.config['DATA_COUNT']
    interval = current_app.config['DATA_INTERCAL']
    d = g.current_user.devices.filter_by(id=device_id).first()
    if d is None:
        return jsonify({'status': 404})
    else:
        s = d.sensors.filter_by(id=sensor_id).first()
        if s is None:
            return jsonify({'status': 404})
        else:
            if request.method == 'GET':
                newdata = s.datas.order_by(Data.id.desc()).first()
                if newdata is None:
                    return jsonify({'status': 404})
                else:
                    return jsonify({'status':200,'data':newdata.to_json()})
            else:
                data_json = request.json
                if data_json is None:
                    return jsonify({'status': 404})
                else:
                    data = data_json.get('data')
                    if data is None:
                        return jsonify({'status': 404})
                    else:
                        old_time = time.mktime(s.datas.order_by(Data.id.desc()).first().time.timetuple())
                        new_time = time.mktime(datetime.utcnow().timetuple())
                        if new_time - old_time < interval:
                            return jsonify({'status': 412,'tip':'请求时间间隔不能低于20s'})
                        else:
                            d = Data()
                            print(s.datas.count())
                            if s.datas.count()+1>count:
                                sd = s.datas.first()
                                db.session.delete(sd)
                            d.sensor_id = sensor_id
                            d.data = data
                            db.session.add(d)


                            alert = Waring()
                            alert.max = s.max
                            alert.min = s.min
                            alert.sensor_id = sensor_id
                            alert.device_id = device_id
                            alert.user_id = g.current_user.id
                            alert.data = d.data
                            if s.max > s.min:
                                if d.data > s.max:
                                    alert.about = '超过上限'
                                    db.session.add(alert)
                                if d.data < s.min:
                                    alert.about = '低于下限'
                                    db.session.add(alert)
                            db.session.commit()

                            return jsonify({'status':200,'success':True})
