from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from wrappers import is_logged_in

dashboard_api = Blueprint('dashboard_api', __name__)
####################################################################
# DASHBOARD


@dashboard_api.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard/dashboard.html')

####################################################################
