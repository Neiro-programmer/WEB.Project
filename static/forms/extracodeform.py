# This Python file uses the following encoding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired


class ExtraCodeForm(FlaskForm):
    code = IntegerField('code', validators=[DataRequired()])
    submit = SubmitField('Отправить код')
