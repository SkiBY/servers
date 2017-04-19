# coding=utf-8 

import os
class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CSRF_ENABLED = True
    SECRET_KEY = 'lsdkjfnzxy345897#cxcm,vnaszz'
    #SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/servers'
    PG_USER = 'postgres'
    PG_PASS = ''


    
