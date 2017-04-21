# coding=utf-8 
#приложение непосредственно

from flask import Flask, redirect, url_for, request, flash
app = Flask(__name__)

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import sqlalchemy_utils
app.config.from_object('config.Config')
db = SQLAlchemy(app)
#from wtforms import Form
from sqlalchemy_utils import ChoiceType


class User(db.Model):
    __tablename__ = 'user'

    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


@app.route('/create_user')
def create_user():
    from bull import app, bcrypt
    user = User(email='root@root.ru', password=bcrypt.generate_password_hash('root'))
    db.session.add(user)
    db.session.commit()
    return u'root added'



#определяем датацентр
class Datacenter(db.Model):
    __tablename__ = 'datacenter'
    tier_choice = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
    ]

    id = db.Column(db.Integer, primary_key=True, )
    name = db.Column(db.String(80), info={'label': u'Имя'}, unique=True, nullable=False)
    address = db.Column(db.String(255), info={'label': u'Адрес'}) 
    slots = db.Column(db.Integer, info={'label': u'Слотов'})
    b_slots = db.Column(db.Integer, info={'label': u'Занятых слотов'}, default=0)
    #tier = db.Column(ChoiceType(tier_choice))
    tier = db.Column(db.Integer, info={'label': u'Tier'})

    # def __init__(self, username, email):
    #     self.username = username
    #     self.email = email
    # @hybrid_property
    # def serv_count(self):
    #     return len(self.servers)
        


    def __repr__(self):
        return '<Datacenter %s>' % self.name

#определяем сервер
class DataServer(db.Model):
    __tablename__ = 'dataserver'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, info={'label': u'Имя'})
    manufacturer = db.Column(db.String(255), nullable=False, info={'label': u'Производитель'}) 
    model = db.Column(db.String(255), nullable=False, info={'label': u'Модель'}) 
    s_number = db.Column(db.String(255), nullable=False, info={'label': u'Серийный номер'}) 
    server_os = db.Column(db.String(255), nullable=False, info={'label': u'ОС'}) 
    datacenter_id = db.Column(db.Integer, db.ForeignKey('datacenter.id'), info={'label': u'Датацентр'})
    datacenter = db.relationship('Datacenter', backref=db.backref('servers', lazy='joined')) 


    
    def __repr__(self):
        return '<Server %r>' % self.name



@app.route('/')
@app.route('/index')
@login_required
def index():
    #user = { 'nickname': 'Miguel' } 
    return render_template("index.html",
        title = 'Home',
        user = 'user',
        )

@app.route('/datacentres')
@login_required
def datacentres(methods=['GET','POST']):
    if request.method == 'GET' and 'sorting' in request.args:
        sorting = request.args.get('sorting')
    else:
        sorting = 'name'
       
    #datacentres = Datacenter.query.order_by('serv_count').all()
    #return u'%s' % [d.serv_count for d in datacentres]
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

@app.route('/servers/')
@app.route('/servers')
@login_required
def servers(methods=['GET']):
    if request.method == 'GET' and 'sorting' in request.args:
        sorting = request.args.get('sorting')
    else:
        sorting = 'name'

    if request.method == 'GET' and 'q' in request.args:
        q_string = request.args.get('q')
    else:
        q_string=None
       
    
    try:
        servers = DataServer.query.order_by(getattr(DataServer, sorting)).all()
        pass
    except:
        servers = DataServer.query.order_by('name').all()

    return render_template("servers.html",
        servers = servers,
        #d_count=Datacenter.query.count(),
        #user = 'user',
        )








@app.route('/edit_dc/<int:dc_id>/', methods=['GET', 'POST'])
@app.route('/add_dc/', methods=['GET', 'POST'])
@login_required
def add_dc(dc_id=None):
    from flask_wtf import FlaskForm
    from wtforms_alchemy import model_form_factory
    ModelForm = model_form_factory(FlaskForm)

    class DataCenterForm(ModelForm):
        class Meta:
            model = Datacenter
            exclude = ['b_slots',]
    

    
    if dc_id:
        dc = Datacenter.query.get_or_404(dc_id)
        if request.method=='POST':
            form = DataCenterForm(request.form, obj=dc)

        else:
            form = DataCenterForm(obj=dc)
    else:
        form = DataCenterForm(request.form)

    if form.validate_on_submit():
        if dc_id:
            form.populate_obj(dc)
            flash(u'Изменен датацентр %s' % dc.name, 'success')
        else:
            dc = Datacenter()
            form.populate_obj(dc)
            db.session.add(dc)
            flash(u'Добавлен датацентр %s' % dc.name, 'success')
            
        db.session.commit()
        
        return redirect(url_for('datacentres'))
    else:
        if form.errors.items():
            for field, errors in form.errors.iteritems():
                for error in errors:
                    flash(u"Ошибка в поле %s: %s" % (
                        getattr(form, field).label.text,
                        error
                    ), 'error')

        if dc_id:
            return render_template("edit_dc.html",
                form = form,
                dc_id=dc_id,
                )
        else:
            return render_template("add_dc.html",
                form = form,
                )


@app.route('/edit_ds/<int:ds_id>/', methods=['GET', 'POST'])
@app.route('/add_ds/<int:dc_id>/', methods=['GET', 'POST'])
@login_required
def add_ds(dc_id=None, ds_id = None):
    if dc_id:
        dc = Datacenter.query.filter_by(id=dc_id).first_or_404()
        c_slots = dc.slots
        s_slots = DataServer.query.filter_by(datacenter_id = dc_id).count()
        if c_slots == s_slots:
            flash(u'В датацентре %s заняты все слоты' % dc.name, 'error')
            return redirect(url_for('view_dc', dc_id=dc_id))

    from flask_wtf import FlaskForm
    from wtforms_alchemy import model_form_factory
    ModelForm = model_form_factory(FlaskForm)

    class DataServerForm(ModelForm):
        class Meta:
            model = DataServer
    

    
    if ds_id:
        ds = DataServer.query.get_or_404(ds_id)
        if request.method=='POST':
            form = DataServerForm(request.form, obj=ds)

        else:
            form = DataServerForm(obj=ds)
    else:
        dc = Datacenter.query.get_or_404(dc_id)
        form = DataServerForm(request.form)

    if form.validate_on_submit():
        if ds_id:
            form.populate_obj(ds)
            flash(u'Изменен сервер %s' % ds.name, 'success')
            dc_id = ds.datacenter_id
        else:
            ds = DataServer()
            form.populate_obj(ds)
            ds.datacenter_id = dc_id
            db.session.add(ds)
            if dc.b_slots:
                dc.b_slots += 1
            else:
                dc.b_slots = 1

            flash(u'Добавлен сервер в датацентр %s' % dc.name, 'success')
            
            
        db.session.commit()
        
        return redirect(url_for('view_dc', dc_id=dc_id))
    else:
        if form.errors.items():
            for field, errors in form.errors.iteritems():
                for error in errors:
                    flash(u"Ошибка в поле %s: %s" % (
                        getattr(form, field).label.text,
                        error
                    ), 'error')

        if ds_id:
            return render_template("edit_ds.html",
                form = form,
                ds_id=ds_id,
                )
        else:
            return render_template("add_ds.html",
                form = form,
                dc_id=dc_id,
                )


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
@login_required
def remove_dc(dc_id):
    dc = Datacenter.query.get_or_404(dc_id)
    db.session.delete(dc)
    db.session.commit()
    return redirect(url_for('datacentres'))

@app.route('/view_dc/<int:dc_id>')
@login_required
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
@login_required
def remove_ds(ds_id):
    ds = DataServer.query.get_or_404(ds_id)
    dc=ds.dataserver_id
    db.session.delete(ds)
    db.session.commit()
    return redirect(url_for('view_dc', dc_id=dc))



