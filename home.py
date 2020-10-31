from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql

home_api = Blueprint('home_api', __name__)


@home_api.route('/')
def index():

    if "logged_in" in session and session["logged_in"]:
        return redirect(url_for("dashboard_api.dashboard"))
    else:
        return render_template('home/home.html')
