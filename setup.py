"""
Flask-QueryInspect
-------------

Flask-QueryInspect is a Flask extension that provides metrics on SQL queries executed for each request.

It assumes use of and relies upon SQLAlchemy as the underlying ORM.

This extension was inspired by internal tooling of this sort, and
then directly by https://github.com/dobarkod/django-queryinspect

"""
from setuptools import setup


setup(
    name='Flask-QueryInspect',
    version='0.1',
    url='https://github.com/noise/flask-queryinspect',
    license='MIT',
    author='Bret Barker',
    author_email='bret@abitrandom.net',
    description='Flask extension to provide metrics on SQL queries per request.',
    long_description=__doc__,
    py_modules=['flask_queryinspect'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'SQLAlchemy'
    ],
    tests_require=[
        'Flask-SQLAlchemy'
    ],
    test_suite='test_queryinspect',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
