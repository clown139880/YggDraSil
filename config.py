# -*- coding: utf-8 -*-
# ...

import os
import sae.const
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, ' db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

#oauth
OAUTH_CREDENTITALS = {
    'weibo': {
        'id': '2957192072',
        'secret': '55874c06581fcc40e9d083c15f984197'
    }
}

# available languages
LANGUAGES = {
    'en': 'ENGLISH',
    'zh': u'简体中文'
}

# baidu translation api
BAIDU_APPID = '20160331000017268'
BAIDU_SECRETKEY = 'vE9gamXRuY51b5So4fsR'

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['you@example.com']

# pagination
POSTS_PER_PAGE = 3

WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50
