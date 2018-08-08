from flask_mail import Message, Mail
from app import mail
from threading import Thread
from flask import current_app


def send_mail_handler(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject, sender, recvers, body, html):
    msg = Message(subject=subject, sender=sender, recipients=recvers)
    if html:
        msg.html = html
    else:
        msg.body = body
    app = current_app._get_current_object()
    thread = Thread(target=send_mail_handler, args=[app, msg])
    thread.start()
