from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, PasswordField, EmailField, DateTimeField, \
    TelField
from wtforms.validators import DataRequired


class AddEventForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    ending_time = StringField('Время окончания в формате часы:минуты, пример: 17:25', validators=[DataRequired()])
    contact = TelField('Введите номер телефона(необ)')
    telegram = StringField('Введите телеграм для контакта(необ)')
    submit = SubmitField('Войти')
