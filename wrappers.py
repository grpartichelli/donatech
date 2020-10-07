from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


#############################################
# WRAPPERS
# Check if user logged_in


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session["logged_in"]:
            return f(*args, **kwargs)
        else:
            flash("Por favor login para poder acessar essa área.", "danger")
            return redirect(url_for("login_api.login"))
    return wrap

# Check if user is admin logged_in


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "role" in session and session["role"] == 'admin':
            return f(*args, **kwargs)
        else:
            flash("Somente Administradores podem acessar essa área", "danger")
            return redirect(url_for("index"))
    return wrap
