from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, PasswordField, EmailField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Optional


class SortingForm(FlaskForm):
    city = StringField('Сортировка по городу', validators=[Optional()], default='Все')
    categ = SelectField('Категория', choices=sorted(
        ['Все', 'Спорт', 'Музыка', 'Искусство', 'Общение', 'Психология', 'Игры', 'Дегустация']),
                        validators=[Optional()], default=0)
    submit = SubmitField('Показать')
