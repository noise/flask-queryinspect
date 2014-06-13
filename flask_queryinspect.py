import logging
import time
from flask import current_app
from sqlalchemy.engine import Engine
from sqlalchemy.event import listen

log = logging.getLogger(__name__)

# Find the stack on which we want to store metrics
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class QueryInspect(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('QUERYINSPECT_ENABLED', True)
        app.config.setdefault('QUERYINSPECT_HEADERS', True)
        app.config.setdefault('QUERYINSPECT_HEADERS_COMBINED', True)
        app.config.setdefault('QUERYINSPECT_LOG', True)

        app.before_request(self.before_request)
        app.after_request(self.after_request)

        listen(Engine, 'connect', self.connect)
        listen(Engine, 'before_cursor_execute', self.before_cursor_execute)
        listen(Engine, 'after_cursor_execute', self.after_cursor_execute)

    def connect(self, dbapi_connection, connection_record):
        if not current_app or not current_app.config.get('QUERYINSPECT_ENABLED'):
            return
        stack.queryinspect['conns'] += 1

    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        if not current_app or not current_app.config.get('QUERYINSPECT_ENABLED'):
            return
        stack.queryinspect['q_start'] = time.time()

    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        if not current_app or not current_app.config.get('QUERYINSPECT_ENABLED'):
            return
        stack.queryinspect['q_time'] += time.time() - stack.queryinspect['q_start']
        if statement.lower().startswith('select'):
            stack.queryinspect['reads'] += 1
        else:
            stack.queryinspect['writes'] += 1

    def before_request(self, *kw1, **kw2):
        if not current_app or not current_app.config.get('QUERYINSPECT_ENABLED'):
            return
        stack.queryinspect = {
            'r_start': time.time(),
            'q_start': 0,
            'r_time': 0,
            'q_time': 0,
            'reads': 0,
            'writes': 0,
            'conns': 0
        }

    def after_request(self, response, *kw1, **kw2):
        if not current_app or not current_app.config.get('QUERYINSPECT_ENABLED'):
            return

        qi = stack.queryinspect
        qi['r_time'] = time.time() - qi['r_start']
        qi['q_time_ms'] = round(qi['q_time'] * 1000, 1)
        qi['r_time_ms'] = round(qi['r_time'] * 1000, 1)

        if current_app.config.get('QUERYINSPECT_LOG'):
            log.info('measure#qi.r_time=%(r_time_ms).1fms, measure#qi.q_time=%(q_time_ms).1fms,' +
                     'count#qi.reads=%(reads)d, count#qi.writes=%(writes)d, count#qi.conns=%(conns)d', qi)

        if current_app.config.get('QUERYINSPECT_HEADERS'):
            if current_app.config.get('QUERYINSPECT_HEADERS_COMBINED'):
                combo = ('reads=%(reads)d,writes=%(writes)d,conns=%(conns)d,q_time=%(q_time_ms).1fms,' +
                         'r_time=%(r_time_ms).1fms') % qi
                response.headers['X-QueryInspect-Combined'] = combo
            else:
                response.headers['X-QueryInspect-Num-SQL-Queries'] = qi['reads'] + qi['writes']
                #response.headers['X-QueryInspect-Duplicate-SQL-Queries'] = qi['dupes']
                response.headers['X-QueryInspect-Total-SQL-Time'] = qi['q_time_ms']
                response.headers['X-QueryInspect-Total-Request-Time'] = qi['r_time_ms']
        return response
