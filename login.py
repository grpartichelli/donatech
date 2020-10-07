from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from passlib.hash import sha256_crypt
from mysqldb import mysql
login_api = Blueprint('login_api', __name__)

########################################################
# LOGIN ROUTE


@login_api.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form["email"]
        password_candidate = request.form["password"]

        # Making a cursor to use the db
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email
                session['role'] = data['role']
                session['name'] = data['name']
                session['userid'] = data['id']

                flash("Você está logado.", "success")

                cur.close()
                return redirect(url_for("dashboard_api.dashboard"))
            else:
                er = "Login falhou."

                cur.close()
                return render_template('login.html', error=er)

        else:
            er = "Email não encontrado."

            cur.close()
            return render_template('login.html', error=er)

        cur.close()
    return render_template('login.html')

###############################################
# LOGOUT


@login_api.route("/logout")
def logout():
    session.clear()
    flash("Você está deslogado", "success")
    session["logged_in"] = False
    return redirect(url_for('login_api.login'))

####################################################################
