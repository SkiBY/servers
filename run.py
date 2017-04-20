# coding=utf-8 
from c_base import app, User
from flask_login import LoginManager, UserMixin, login_required, login_manager, login_user, logout_user 
from flask import Response, redirect, url_for, request, session, abort

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.

    l_m = u'<p>Введите данные для входа</p>'
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).count()==1:
            user=User.query.filter_by(email=email).first()
            if password == user.password:
                user.authenticated = True
                login_user(user, remember=True)

                return redirect(url_for('index'))
        l_m = u'<p>Введите верные почту и пароль</p>'
               
    
    return Response('''%s
    <form class = "loginform" action="/login/" method="post">
        <p><input type=text name=email>
        <p><input type=password name=password>
        <p><input type=submit value=Login>
    </form>
    ''' % l_m)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Вы вышли из системы</p>')


app.debug = True
app.run()