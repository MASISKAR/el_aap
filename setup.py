from setuptools import setup

setup(
    name='el_aap',
    version='0.0.1',
    description='Elasticsearch Authentication and Authorization Proxy',
    long_description="""
Elasticsearch Authentication and Authorization reverse proxy
implementation in Python 3.

Copyright (c) 2015, Stephan Schultchen.

License: MIT (see LICENSE for details)
    """,
    packages=['el_aap', 'el_aap_api'],
    url='https://github.com/schlitzered/pyredis',
    license='MIT',
    author='schlitzer',
    author_email='stephan.schultchen@gmail.com',
    test_suite='test',
    platforms='posix',
    classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
    ],
    install_requires=[
        'bottle',
        'cachetools',
        'pep3143daemon',
        'pymongo',
        'requests',
        'waitress',
        'wsgi-request-logger',
        'validation'
    ],
    keywords=[
        'elasticsearch'
    ]
)