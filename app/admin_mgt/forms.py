from flask_wtf import FlaskForm as Form, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email


class LoginForm(Form):
    username = StringField('Имя пользователя', [DataRequired()]) # , Email()])
    secret = PasswordField('Пароль', [DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class RegisterForm(Form):
    name = StringField('NickName', [DataRequired()])
    email = StringField('Email address', [DataRequired()]) #, Email()])
    password = PasswordField('Password', [DataRequired()])
    confirm = PasswordField('Repeat Password', [
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    accept_tos = BooleanField('I accept the TOS', [DataRequired()])
    recaptcha = RecaptchaField()
