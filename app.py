from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# COnfig MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'donatech'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)


#############################################################################
# HOME ROUTE


@app.route('/')
def index():
    if session["logged_in"]:
        return redirect(url_for("dashboard"))
    return render_template('home.html')

#################################################################################
# REGISTER ROUTE


class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    cpf = StringField('CPF', [validators.Length(min=11, max=11)])
    password = PasswordField('Password', [validators.Length(min=4, max=50)])


@app.route('/register', methods=['GET', 'POST'])
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
        redirect(url_for("index"))
    return render_template('register.html', form=form)


########################################################
# LOGIN ROUTE
@app.route('/login', methods=['GET', 'POST'])
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
                session['rolate'] = data['role']
                session['name'] = data['name']

                flash("Você está logado.", "success")

                cur.close()
                return redirect(url_for("dashboard"))
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
####################################################################

# Check if user logged_in


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session["logged_in"]:
            return f(*args, **kwargs)
        else:
            flash("Por favor login para poder acessar essa área.", "danger")
            return redirect(url_for("login"))
    return wrap


####################################################################
# DASHBOARD


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


#################################
# LOGOUT


@app.route("/logout")
def logout():
    session.clear()
    flash("Você está logout.", "success")
    session["logged_in"] = False
    return redirect(url_for('login'))


app.secret_key = 'super secret key'
if __name__ == '__main__':
    app.run(debug=True)
