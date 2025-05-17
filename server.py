import os
import string
from datetime import datetime
from os import abort
from random import shuffle, sample, random, choices, randint
import sqlalchemy
from flask import url_for, Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data.db_session import global_init
from data import db_session
from data.events import Event
from data.users import User
from mail_sender import send_email
from static.forms.edit_event_form import EditEventForm
from static.forms.edit_profile_info import EditProfile
from static.forms.extracodeform import ExtraCodeForm
from static.forms.loginform import LoginForm
from static.forms.registerform import RegisterForm
from static.forms.add_event_form import AddEventForm
from static.forms.sorting_city_name import SortingForm
from dotenv import load_dotenv
import os
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase
from flask import session
from cities import get_cities

app = Flask(__name__)
ADMINS_ID = [1, 2]
MODERATORS_ID = [3]
load_dotenv()


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
    return s


app.secret_key = make_secret_key()
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
    return render_template("login.html", form=form)
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
        # db_sess.add(user)
        # db_sess.commit()
        db_sess.add(user)
        db_sess.commit()
        print("Redirecting to home page...")
        return redirect('/')

    else:
        return render_template('register.html', message="Неправильные данные", form=form)
    return render_template('register.html', message="Пожалуйста, введите данные о себе", form=form)


# @app.route('/extra_code/<email>/<extrac>', methods=['GET', 'POST'])
# def generate_extra_code(email, extrac):
#     global us
#     form = ExtraCodeForm()
#     extra = session.get('extracode')
#     res = send_email(email, 'NearMe_code',
#                      f'''Введите 6-значный код на нашем сайте NearMe, чтобы подтвердить вашу регистрацию.
# Код для подтверждения регистрации: {extra}
# Не сообщайте код никому!''', [])
#     if form.validate_on_submit() and res:
#         code = form.code.data
#         if code == extra:
#             db_sess = db_session.create_session()
#             db_sess.add(us)
#             db_sess.commit()
#             send_email(email, 'NearMe',
#                        'Если вам пришло это письмо, то вы успешно зарегистрировались на нашем сайте NearMe!',
#                        ['kartina.jpg'])
#             us = None
#             # НУЖНО ЧТОБЫ ПЕРЕКИДЫВАЛ НА СТРАНИЦУ С ПРОФИЛЕМ, А НЕ НА ПЕРВУЮ
#             return redirect("/")
#         else:
#             return render_template('extra_code.html', message="Коды не совпали, введите код повторно", mail=email,
#                                    form=form)
#     elif not res:
#         return render_template('extra_code.html',
#                                message=f"Письмо не было доставлено, так его распознали, как спам, для регистрации "
#                                        f"используйте почту mail.ru, yandex.ru, list.ru или напишите в тг: @iDotrey",
#                                mail=email,
#                                form=form)
#     return render_template("extra_code.html", mail=email, form=form)


@app.errorhandler(404)
def page_not_found(e):
    return 'Не найдена страница, пожалуйста, вернитесь назад'


@app.errorhandler(400)
def icorrrect_request(e):
    return f'Некорректный запрос, пожалуйста, попробуйте снова, {e}'


@app.route('/events', methods=['GET', 'POST'])
def add_events():
    form = SortingForm()
    db_sess = db_session.create_session()
    if form.city.data == 'Все' and form.categ.data == 'Все':
        events = db_sess.query(Event).all()
    elif form.city.data != 'Все' and form.categ.data == 'Все':
        events = db_sess.query(Event).filter(Event.cities == form.city.data.capitalize()).all()
    elif form.city.data == 'Все' and form.categ.data != 'Все':
        events = db_sess.query(Event).filter(Event.category == form.categ.data).all()
    elif form.city.data != 'Все' and form.categ.data != 'Все':
        events = db_sess.query(Event).filter(Event.category == form.categ.data,
                                             Event.cities == form.city.data.capitalize()).all()
    return render_template('events.html', events=events, moderators=MODERATORS_ID, admins=ADMINS_ID, form=form)


@login_required
@app.route('/events/<int:id>', methods=['GET', 'POST'])
def events_user(id):
    db_sess = db_session.create_session()
    form = SortingForm()
    if form.city.data == 'Все' and form.categ.data == 'Все':
        events = db_sess.query(Event).filter(Event.user_id == id).all()
    elif form.city.data != 'Все' and form.categ.data == 'Все':
        events = db_sess.query(Event).filter(Event.cities == form.city.data.capitalize(), Event.user_id == id).all()
    elif form.city.data == 'Все' and form.categ.data != 'Все':
        events = db_sess.query(Event).filter(Event.category == form.categ.data, Event.user_id == id).all()
    elif form.city.data != 'Все' and form.categ.data != 'Все':
        events = db_sess.query(Event).filter(Event.category == form.categ.data,
                                             Event.cities == form.city.data.capitalize(), Event.user_id == id).all()
    return render_template('events.html', events=events, moderators=MODERATORS_ID, admins=ADMINS_ID, form=form)


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
            user_id=current_user.id,
            category=form.category.data,
        )
        try:
            # Нужно прописать, чтобы была ещё дата и время начала события, важно!!!!
            # Желательно ещё маркировать прошедшие и предстоящие события, по фозможности фильтровать или хотя бы размещать по релевантности
            ending_time = form.ending_time.data
            hh, mm = ending_time.split(':')
            if int(hh) < 24 and int(mm) < 60 and int(hh) >= 0 and int(mm) >= 0:
                event.ending_time = form.ending_time.data
            else:
                return render_template('add_event_form.html', form=form,
                                       message='Неправильный формат времени окончания')
        except Exception:
            return render_template('add_event_form.html', form=form, message='Неправильный формат времени окончания')
        f = form.file.data
        if f:
            random_number = ''.join(choices('0123456789', k=10))
            path = os.path.join('..', 'static', 'img') + '/' + str(current_user.id) + str(random_number) + '.png'
            while os.path.exists(path):
                random_number = ''.join(choices('0123456789', k=10))
                path = '../static/img' + str(current_user.id) + str(random_number)
            with open(path[3:], 'wb') as file:
                file.write(f.read())
            event.file = path
            fl = False
            for i in get_cities():
                if i in form.location.data or i.lower() in form.location.data:
                    event.cities = i
                    fl = True
                    break
            if not fl:
                return render_template('add_event_form.html', form=form, title='Добавление события',
                                       message='Неправильный формат локации: укажите название города с большой или маленькой буквы, после этого через запятую улицу')
            else:
                event.location = form.location.data
                current_user.events.append(event)
                db_sess.merge(current_user)
                db_sess.commit()
                return redirect("/events")
        else:
            fl = False
            for i in get_cities():
                if i in form.location.data or i.lower() in form.location.data:
                    event.cities = i
                    fl = True
                    break
            if not fl:
                return render_template('add_event_form.html', form=form, title='Добавление события',
                                       message='Неправильный формат локации: укажите название города с большой или маленькой буквы, после этого через запятую улицу')
            path = '../static/img/default.png'
            event.file = path
            event.location = form.location.data
            current_user.events.append(event)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect("/events")
    return render_template('add_event_form.html', form=form, title='Добавление события')


@app.route('/edit/event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    form = EditEventForm()
    path = ''
    if request.method == "GET":
        db_sess = db_session.create_session()
        event = db_sess.query(Event).filter(Event.id == id, (
                (Event.user == current_user) | (current_user.id in ADMINS_ID) | (
                current_user.id in MODERATORS_ID))).first()
        if event:
            form.name.data = event.name
            form.description.data = event.description
            form.contact.data = event.contact
            form.telegram.data = event.telegram
            form.ending_time.data = event.ending_time
            form.category.data = event.category
            form.location.data = event.location
            path = event.file
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        event = db_sess.query(Event).filter(Event.id == id, (
                (Event.user == current_user) | (current_user.id in ADMINS_ID) | (
                current_user.id in MODERATORS_ID))).first()
        if event:
            event.name = form.name.data
            event.description = form.description.data
            event.contact = form.contact.data
            event.telegram = form.telegram.data
            event.ending_time = form.ending_time.data
            event.category = form.category.data
            f = form.file.data
            if f:
                random_number = ''.join(choices('0123456789', k=10))
                path = os.path.join('..', 'static', 'img') + '/' + str(current_user.id) + str(random_number) + '.png'
                while os.path.exists(path):
                    random_number = ''.join(choices('0123456789', k=10))
                    path = '../static/img' + str(current_user.id) + str(random_number)
                with open(path[3:], 'wb') as file:
                    file.write(f.read())
                event.file = path
                fl = False
                for i in get_cities():
                    if i in form.location.data or i.lower() in form.location.data:
                        event.cities = i
                        fl = True
                if not fl:
                    return render_template('add_event_form.html', form=form, title='Добавление события',
                                           message='Неправильный формат локации: укажите название города с большой или маленькой буквы')
                event.location = form.location.data
                db_sess.commit()
            else:
                fl = False
                for i in get_cities():
                    if i in form.location.data or i.lower() in form.location.data:
                        event.cities = i
                        fl = True
                if not fl:
                    return render_template('add_event_form.html', form=form, title='Добавление события',
                                           message='Неправильный формат локации: укажите название города с большой или маленькой буквы')
                event.location = form.location.data
                db_sess.commit()
                return redirect("/events")
        else:
            abort(404)
    return render_template('edit_event_form.html', title="Редактирование события", form=form, path=path)


@app.route('/delete/event/<int:id>', methods=['GET', 'POST'])
def delete_event(id):
    db_sess = db_session.create_session()
    event = db_sess.query(Event).filter(Event.id == id, (
            (Event.user == current_user) | (current_user.id in ADMINS_ID) | (
            current_user.id in MODERATORS_ID))).first()
    if event:
        db_sess.delete(event)
        db_sess.commit()
        return redirect("/events")
    else:
        abort(404)


@app.route('/get_route/event/<id>', methods=['GET', 'POST'])
def get_route_event(id):
    db_sess = db_session.create_session()
    event = db_sess.query(Event).filter(Event.id == id).first()
    if not event:
        abort(404)
    else:
        location = event.location
        return render_template('get_route.html', location=location)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    form = EditProfile()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if not user:
            abort(404)
        else:
            form.name.data = user.name
            form.surname.data = user.surname
            form.password.data = 'Пароль зашифрован и не будет показан, но вы можете его изменить'
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if not user:
            abort(404)
        else:
            user.name = form.name.data
            user.surname = form.surname.data
            if form.password.data != 'Пароль зашифрован и не будет показан, но вы можете его изменить':
                user.set_password(form.password.data)
            db_sess.commit()
            return redirect("/")
    else:
        print(form.errors)
    return render_template('profile.html', form=form)


if __name__ == '__main__':
    global_init('db/near_me.sqlite')
    serve(app, port=5000, host='127.0.0.1')
