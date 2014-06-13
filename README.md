# Flask QueryInspect Extension

[![Build Status](https://travis-ci.org/noise/flask-queryinspect.svg?branch=master)](https://travis-ci.org/noise/flask-queryinspect?branch=master)

Flask-QueryInspect is a Flask extension that provides metrics on SQL queries executed for each request.

It assumes use of and relies upon SQLAlchemy as the underlying ORM.

I've used this method for several Flask projects and was finally inspired to turn it into an extension after seeing
https://github.com/dobarkod/django-queryinspect.

Flask-QueryInspect tracks the count of SQL reads and writes, new DB connections, and total request and total query time for each request. It does not yet handle reporting of duplicate queries like Django-QueryInspect.

# Installation #

```
pip install Flask-QueryInspect
```

## Usage ##

```python
app = Flask(__name__)
qi = QueryInspect(app)
```

## Configuration ##

QueryInspect has the following optional config vars that can be set in
Flask's app.config:

Variable | Default | Description
------------- | ------------- | -------------
QUERYINSPECT_ENABLED | True | False to completely disable QueryInspect
QUERYINSPECT_HEADERS | True | Enable response header injection
QUERYINSPECT_HEADERS_COMBINED | True | Enable combined single header, else use [Django QueryInspect's](https://github.com/dobarkod/django-queryinspect) style
QUERYINSPECT_LOG | True | Enable logging, in Librato style

## Combined Header Format ##

```
X-QueryInspect-Combined: reads=1,writes=1,conns=0,q_time=0.2ms,r_time=2.9ms
```

## Log Format ##

Logging is output using the standard Python logging module (logger name is 'flask_queryinspect') and formatted so it can be easily read by Librato, see: https://devcenter.heroku.com/articles/librato#custom-log-based-metrics

E.g.:
```
INFO measure#qi.r_time=2.9ms, measure#qi.q_time=0.2ms,count#qi.reads=1, count#qi.writes=1, count#qi.conns=0
```

## Example App ##

Run the example server:

```
python example_app.py
```

And in another terminal:

```
curl -D - http://127.0.0.1:5000/
```

Notice the X-QueryInspect-Combined header.
