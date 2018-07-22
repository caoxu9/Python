'''
发送邮件
'''

from threading import Thread
from app import mail,app
from flask_mail import Message



def send(app,msg):
    with app.app_context():
        mail.send(msg)
def send_mail_fun(subject,recipients,sender,html):
    msg = Message(subject=subject,sender=sender,recipients=recipients,html=html)
    th = Thread(target=send,args=(app,msg))
    th.start()

@app.route('/')
def index():
    send_mail_fun(subject='你猜我是谁',sender='发送者邮箱',recipients=['接受者邮箱，可为列表'],html='<a href="http://www.baidu.com"><button>点我笨蛋</button></a>')
    return 'ok'