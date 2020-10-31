from flask import Blueprint, Flask, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


register_api = Blueprint('register_api', __name__)
#################################################################################
# REGISTER ROUTE


class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    cpf = StringField('CPF', [validators.Length(min=11, max=11)])
    password = PasswordField('Password', [validators.Length(min=4, max=50)])


@register_api.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        cpf = form.cpf.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Making a cursor to change the db
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(email, name, password, role, cpf) VALUES(%s,%s,%s,%s,%s)",
                    (email, name, password, "default", cpf))
        mysql.connection.commit()
        cur.close()
        flash("Você foi cadastrado com sucesso", "success")
        redirect(url_for("home_api.index"))
    return render_template('register/register.html', form=form)
