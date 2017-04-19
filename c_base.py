# coding=utf-8 
#приложение непосредственно

from flask import Flask, redirect, url_for, request
app = Flask(__name__)
from flask import render_template, request

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy_utils
app.config.from_object('config.Config')
db = SQLAlchemy(app)

from sqlalchemy_utils import ChoiceType

#определяем датацентр
class Datacenter(db.Model):
    __tablename__ = 'datacenter'
    tier_choice = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False,)
    address = db.Column(db.String(255)) 
    slots = db.Column(db.Integer, )
    #tier = db.Column(ChoiceType(tier_choice))
    tier = db.Column(db.Integer,)

    # def __init__(self, username, email):
    #     self.username = username
    #     self.email = email

    def __repr__(self):
        return '<Datacenter %s>' % self.name

#определяем сервер
class DataServer(db.Model):
    __tablename__ = 'dataserver'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False,)
    address = db.Column(db.String(255), nullable=False,) 
    manufacturer = db.Column(db.String(255), nullable=False,) 
    model = db.Column(db.String(255), nullable=False,) 
    s_number = db.Column(db.String(255), nullable=False,) 
    server_os = db.Column(db.String(255), nullable=False,) 
    datacenter_id = db.Column(db.Integer, db.ForeignKey('datacenter.id'))
    datacenter = db.relationship('Datacenter', backref=db.backref('servers', lazy='joined')) 


    
    def __repr__(self):
        return '<Server %r>' % self.name



@app.route('/')
@app.route('/index')
def index():
    #user = { 'nickname': 'Miguel' } 
    return render_template("index.html",
        title = 'Home',
        user = 'user',
        )

@app.route('/datacentres')
def datacentres(methods=['GET','POST']):
    if request.method == 'GET' and 'sorting' in request.args:
        sorting = request.args.get('sorting')
    else:
        sorting = 'name'
       
    
    try:
        datacentres = Datacenter.query.order_by(getattr(Datacenter, sorting)).all()
        pass
    except:
        datacentres = Datacenter.query.order_by('name').all()

    return render_template("datacentres.html",
        datacentres = datacentres,
        #d_count=Datacenter.query.count(),
        #user = 'user',
        )



# Create our database model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<E-mail %r>' % self.email



@app.route('/add_dc')
def add_dc():
    dc = Datacenter(name='DC0', address=u'Малая Бронная', slots=2, tier = u'2')
    db.session.add(dc)
    db.session.commit()
    return redirect(url_for('datacentres'))
    

