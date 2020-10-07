from flask import Flask
from mysqldb import mysql
######################################################################################
# My imports

from home import home_api
from login import login_api
from register import register_api
from dashboard import dashboard_api
from admin import admin_api
from donor import donor_api
from donee import donee_api

app = Flask(__name__)

######################################################################################
# Config MySQL

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'donatech'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"
mysql.init_app(app)

#################################################################################
#  Registering blueprints

app.register_blueprint(home_api)
app.register_blueprint(login_api)
app.register_blueprint(register_api)
app.register_blueprint(dashboard_api)
app.register_blueprint(admin_api)
app.register_blueprint(donor_api)
app.register_blueprint(donee_api)

#############################################################################

app.secret_key = 'super secret key'
if __name__ == '__main__':
    app.run(debug=True)
