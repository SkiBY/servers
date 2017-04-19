# coding=utf-8 
#приложение непосредственно

from flask import Flask, redirect, url_for, request, flash
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

    id = db.Column(db.Integer, primary_key=True, )
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.Text(255)) 
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



@app.route('/add_dc/', methods=['GET', 'POST'])
def add_dc():
    from wtforms import Form, TextField, IntegerField, DateField, BooleanField, StringField, PasswordField, validators
    #from wtforms_alchemy import Unique
    class DCForm(Form):

        name = TextField(validators=[validators.Required(message=u'Обязательное поле')], label=u'Имя')
        address = TextField(validators=[validators.Required(message=u'Обязательное поле')], label=u'Адрес')
        slots = IntegerField(validators=[validators.Required(message=u'Обязательное поле'), validators.NumberRange(min=1)], label=u'Кол-во слотов')
        tier = IntegerField(validators=[validators.Required(message=u'Обязательное поле'), validators.NumberRange(min=1,max=3, message=u'1, 2 или 3' )], label=u'Tier')

        def validate_name(form, field):
            if Datacenter.query.filter_by(name=field.data).first():
                raise validators.ValidationError(u'Датацентр с таким именем уже существует')
        

    # from wtforms.ext.sqlalchemy.orm import model_form
    # exclude = ['id', ]
    # DCForm = model_form(Datacenter, Form, exclude=exclude, field_args = {
    #     'slots' : {
    #     'label':u'Слоты',
    #     'validators' : [validators.NumberRange(min=1),],
    #             },
    #     'name' : {
    #     'label':u'Имя центра',
    #             },
    #     'address' : {
    #     'label':u'Адрес',
    #             },
    #     'tier' : {
    #     'label':u'Tier',
    #     'validators' : [validators.NumberRange(min=1, max=3, message='1, 2 или 3'),],
    #             },

    #     } )
    
    form = DCForm(request.form)

    
    if request.method == 'POST' and form.validate():
        dc = Datacenter(
            name=form.name.data,
            address=form.address.data,
            slots = form.slots.data,
            tier=form.tier.data,
            )
        db.session.add(dc)
        db.session.commit()

        flash(u'Добавлен датацентр %s' % dc.name, 'success')
        return redirect(url_for('datacentres'))
    else:
        if form.errors.items():
            for field, errors in form.errors.iteritems():
                for error in errors:
                    flash(u"Ошибка в поле %s: %s" % (
                        getattr(form, field).label.text,
                        error
                    ), 'error')

        return render_template("add_dc.html",
            form = form,
            )

    


    #проверка, есть ли такой ДЦ
    dc = Datacenter.query.get_or_404(dc_id)
    ds = DataServer(name='SRV8', manufacturer='Sun', model='1XNA', s_number='SN1267813', server_os='CentOS', datacenter_id=dc_id)
    db.session.add(ds)
    db.session.commit()
    return redirect(url_for('view_dc', dc_id=dc_id))


@app.route('/add_ds/<int:dc_id>/', methods=['GET', 'POST'])
def add_ds(dc_id):
    from wtforms import Form, TextField, IntegerField, DateField, BooleanField, StringField, PasswordField, validators
    #from wtforms_alchemy import Unique
    #для начала проверим, заняты ли слоты
    dc = Datacenter.query.filter_by(id=dc_id).first_or_404()
    c_slots = dc.slots
    s_slots = DataServer.query.filter_by(datacenter_id = dc_id).count()
    if c_slots == s_slots:
        flash(u'В датацентре %s заняты все слоты' % dc.name, 'error')
        return redirect(url_for('view_dc', dc_id=dc_id))

    class DSForm(Form):
        name = StringField(validators=[validators.Required(message=u'Обязательное поле')], label=u'Имя')
        manufacturer = StringField(validators=[validators.Required(message=u'Обязательное поле')], label=u'Производитель')
        model = StringField(validators=[validators.Required(message=u'Обязательное поле')], label=u'Модель')
        s_number = StringField(validators=[validators.Required(message=u'Обязательное поле')], label=u'Серийный номер')
        server_os = StringField(validators=[validators.Required(message=u'Обязательное поле')], label=u'Оп.система')
        
        
                    

    # from wtforms.ext.sqlalchemy.orm import model_form
    # exclude = ['id', ]
    # DCForm = model_form(Datacenter, Form, exclude=exclude, field_args = {
    #     'slots' : {
    #     'label':u'Слоты',
    #     'validators' : [validators.NumberRange(min=1),],
    #             },
    #     'name' : {
    #     'label':u'Имя центра',
    #             },
    #     'address' : {
    #     'label':u'Адрес',
    #             },
    #     'tier' : {
    #     'label':u'Tier',
    #     'validators' : [validators.NumberRange(min=1, max=3, message='1, 2 или 3'),],
    #             },

    #     } )
    
    form = DSForm(request.form)

    
    if request.method == 'POST' and form.validate():
        ds = DataServer(
            name=form.name.data,
            manufacturer=form.manufacturer.data,
            model = form.model.data,
            s_number=form.s_number.data,
            server_os = form.server_os.data,
            datacenter_id=dc_id,
            )
        db.session.add(ds)
        db.session.commit()

        flash(u'Добавлен сервер в датацентр %s' % dc.name, 'success')
        return redirect(url_for('view_dc', dc_id=dc_id))
    else:
        if form.errors.items():
            for field, errors in form.errors.iteritems():
                for error in errors:
                    flash(u"Ошибка в поле %s: %s" % (
                        getattr(form, field).label.text,
                        error
                    ), 'error')

        return render_template("add_ds.html",
            form = form,
            dc_id=dc_id,
            )

    

    

@app.route('/remove_dc/<int:dc_id>')
def remove_dc(dc_id):
    dc = Datacenter.query.get_or_404(dc_id)
    db.session.delete(dc)
    db.session.commit()
    return redirect(url_for('datacentres'))

@app.route('/view_dc/<int:dc_id>')
def view_dc(dc_id):
    dc = Datacenter.query.get_or_404(dc_id)
    if request.method == 'GET' and 'sorting' in request.args:
        sorting = request.args.get('sorting')
    else:
        sorting = 'id'
       
    
    try:
        d_servers = DataServer.query.filter_by(datacenter_id=dc.id).order_by(getattr(DataServer, sorting))
        pass
    except:
        d_servers = DataServer.query.filter_by(datacenter_id=dc.id).order_by('id')    

    
    return render_template("datacenter_view.html",
        datacenter = dc,
        d_servers = d_servers,
        #user = 'user',
        )


@app.route('/remove_ds/<int:ds_id>')
def remove_ds(ds_id):
    ds = DataServer.query.get_or_404(ds_id)
    dc=ds.dataserver_id
    db.session.delete(ds)
    db.session.commit()
    return redirect(url_for('view_dc', dc_id=dc))