import sqlalchemy
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data.db_session import global_init
from data import db_session
from data.users import User
from static.forms.loginform import LoginForm

app = Flask(__name__)


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
    print(s)


make_secret_key()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template("base.html")


@app.route('/login')
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


if __name__ == '__main__':
    global_init('db/near_me.sqlite')
    app.run(port=8080, host='127.0.0.1')
