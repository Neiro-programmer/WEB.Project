import string
from datetime import datetime
from random import shuffle, sample

import sqlalchemy
from flask import url_for, Flask, render_template, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data.db_session import global_init
from data import db_session
from data.events import Event
from data.users import User
from static.forms.loginform import LoginForm
from static.forms.registerform import RegisterForm
from static.forms.add_event_form import AddEventForm

app = Flask(__name__)
ADMINS_ID = [1, 2]
MODERATORS_ID = [3]


def make_secret_key():
    s = ''
    a = list(string.ascii_lowercase)
    a.extend(string.ascii_uppercase)
    a.extend(string.digits)
    for i in range(3):
        shuffle(a)
    for i in sample(a, 25):
        s += i
    app.config['SECRET_KEY'] = s


make_secret_key()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    return render_template("base.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template("login.html", message="Пользователь не найден", form=form)
        elif not user.check_password(form.password.data):
            return render_template('login.html', message="Неправильный пароль", form=form)
        elif user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            return render_template('register.html', message="Пользователь с таким email уже существует", form=form)
        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/")
    return render_template('register.html', message="Пожалуйста, введите данные о себе", form=form)


@app.route('/events', methods=['GET', 'POST'])
def add_events():
    db_sess = db_session.create_session()
    events = db_sess.query(Event).all()
    return render_template('events.html', events=events, moderators=MODERATORS_ID, admins=ADMINS_ID)


@app.route('/add/event', methods=['GET', 'POST'])
def add_event():
    form = AddEventForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        event = Event(
            name=form.name.data,
            description=form.description.data,
            starting_time=datetime.now(),
            contact=form.contact.data,
            telegram=form.telegram.data,
            user_id=current_user.id
        )
        try:
            ending_time = form.ending_time.data
            hh, mm = ending_time.split(':')
            if int(hh) < 24 and int(mm) < 60 and int(hh) >= 0 and int(mm) >= 0:
                event.ending_time = form.ending_time.data
            else:
                return render_template('add_event_form.html', form=form,
                                       message='Неправильный формат времени окончания')
        except Exception:
            return render_template('add_event_form.html', form=form, message='Неправильный формат времени окончания')
        current_user.events.append(event)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect("/")
    return render_template('add_event_form.html', form=form)


if __name__ == '__main__':
    global_init('db/near_me.sqlite')
    app.run(port=8080, host='127.0.0.1')
