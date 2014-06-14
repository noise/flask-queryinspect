import logging
import time
import unittest
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.queryinspect import QueryInspect

log = logging.getLogger(__name__)


class TestQueryInspect(unittest.TestCase):
    app = None

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format='%(asctime)-15s %(levelname)s %(message)s')
        logging.getLogger('flask_queryinspect').setLevel(logging.DEBUG)
        logging.getLogger('test_queryinspect').setLevel(logging.DEBUG)

        TestQueryInspect.app = Flask(__name__)
        TestQueryInspect.app.config['TESTING'] = True

        TestQueryInspect.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        #TestQueryInspect.app.config['SQLALCHEMY_ECHO'] = True
        db = SQLAlchemy(TestQueryInspect.app)
        QueryInspect(TestQueryInspect.app)

        class TestModel(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            foo = db.Column(db.Unicode(10))

            def __init__(self, foo):
                self.foo = foo

        db.create_all(app=TestQueryInspect.app)
        for i in range(10):
            db.session.add(TestModel('test_%d' % i))
        db.session.commit()

        @TestQueryInspect.app.route('/')
        def index():
            return u'No Queries'

        @TestQueryInspect.app.route('/mix')
        def mix():
            t = TestModel.query.first()
            t.foo = 'bar'
            db.session.commit()
            return u'Reads and writes'

        @TestQueryInspect.app.route('/slow')
        def slow():
            time.sleep(.1)
            return u'Slow request'

    def test_noqueries(self):
        with TestQueryInspect.app.test_client() as c:
            res = c.get('/')
            log.debug(res.headers)
            self.assertTrue(res.headers['X-QueryInspect-Combined'].startswith('reads=0,writes=0,conns=0'))

    def test_mix(self):
        with TestQueryInspect.app.test_client() as c:
            res = c.get('/mix')
            log.debug(res.headers)
            self.assertTrue(res.headers['X-QueryInspect-Combined'].startswith('reads=1,writes=1'))

    def test_rtime(self):
        TestQueryInspect.app.config['QUERYINSPECT_HEADERS_COMBINED'] = False
        with TestQueryInspect.app.test_client() as c:
            res = c.get('/slow')
            log.debug(res.headers)
            r_time = float(res.headers['X-QueryInspect-Total-Request-Time'])
            log.debug('r_time: %r', r_time)
            self.assertTrue(90.0 < r_time < 110.0)
        TestQueryInspect.app.config['QUERYINSPECT_HEADERS_COMBINED'] = True
