import requests,chardet,json,time
from ftfy import fix_text
from flask import jsonify


a = 'eyJhbGciOiJIUzI1NiIsImlhdCI6MTUzMzQ1NjA0MCwiZXhwIjoxODQ4ODE2MDQwfQ.eyJpZCI6MX0.C8_6MrlWF55BFyThde3a24oxhCZz33l4Vk5WtSjrNpU'
b = ''
def get_status(token,password):
    header = {'content-type': 'application/json'}
    auth = (token,password)
    for i in range(150):
        data ={'data':int(i)+0.5}
        req = requests.post('http://127.0.0.1:5000/api/1.0/device/3/sensor/5/data',auth=auth,headers=header,data=json.dumps(data))
        print(fix_text(req.text))
        time.sleep(1.5)
get_status(a,b)

