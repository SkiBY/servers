# coding=utf-8 

import os
class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CSRF_ENABLED = True
    SECRET_KEY = 'lsdkjfnzxy345897#cxcm,vnaszz'
    PG_USER = 'postgres'
    PG_PASS = 'postgres'
    PG_BASE_NAME = 'servers'
    SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@localhost/%s' % (PG_USER, PG_PASS, PG_BASE_NAME)
    


    
