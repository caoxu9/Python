class Config:
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'www.uplooking.com'
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = '587'
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'itsdangerous@foxmail.com'
    MAIL_PASSWORD = 'ociuaxqsfvrxdhia'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/flask'


class TestConfig(Config):
    TEST = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/flask'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/flask'


config = {
    'develop': DevelopConfig,
    'test': TestConfig,
    'product': ProductionConfig,
    'default': DevelopConfig,
}
