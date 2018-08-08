class Config:
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'www.uplooking.com'
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = '587'
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'xxxxxx'
    MAIL_PASSWORD = 'xxxxxxx'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #设置时间间隔
    DATA_COUNT = 100
    DATA_INTERCAL = 20


class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/iot'


class TestConfig(Config):
    TEST = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/iot'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/iot'


config = {
    'develop': DevelopConfig,
    'test': TestConfig,
    'product': ProductionConfig,
    'default': DevelopConfig,
}
