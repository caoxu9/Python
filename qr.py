'''
生成二维码
'''
import qrcode

def make_qrcode(value):
    img = qrcode.make(value)
    return img

img = make_qrcode('http://www.baidu.com')
with open('test.png','wb') as f:
    img.save(f)