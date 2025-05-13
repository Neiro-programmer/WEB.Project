from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, PasswordField, EmailField, DateTimeField, \
    TelField, FileField, SelectField
from wtforms.validators import DataRequired, Optional


class AddEventForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    ending_time = StringField('Время окончания в формате часы:минуты, пример: 17:25', validators=[DataRequired()])
    contact = TelField('Введите номер телефона(необ)', validators=[Optional()])
    telegram = StringField('Введите телеграм для контакта(необ)', validators=[Optional()])
    file = FileField('Выберите фотографию(необ)', validators=[Optional()])
    category = SelectField('Категория', choices=sorted(
        ['Все', 'Спорт', 'Музыка', 'Искусство', 'Общение', 'Психология', 'Игры', 'Дегустация']),
                           validators=[DataRequired()])
    location = StringField('Местоположение')

    submit = SubmitField('Добавить')
