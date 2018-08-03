import unittest
from flask import current_app
from app import db, create_app


class TestClass(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_test(self):
        self.assertTrue(current_app.config['TEST'])

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


from app.models import User


class TestModel(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_password_set(self):
        u = User()
        u.name = '张三'
        u.password = '123456'
        self.assertTrue(u.password_hash is not None)

    def test_password_get(self):
        u = User()
        u.name = '李四'
        u.password = '12356'
        with self.assertRaises(AttributeError):
            u.password

    def test_check_password(self):
        u = User()
        u.name = 'wangwu'
        u.password = '1234567'
        self.assertTrue(u.check_password('1234567'))

    def test_password_random(self):
        u = User()
        u.name = 'wangwu'
        u.password = '1234567'
        u1 = User()
        u1.name = 'wangwu'
        u1.password = '1234567'
        self.assertTrue(u.password_hash == u.password_hash)
