from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


app = Flask(__name__)

# COnfig MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'donatech'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)
# HOME ROUTE


@app.route('/')
def index():
    return render_template('home.html')


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

# LOGIN ROUTE


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form["email"]
        password_candidate = request.form["password"]
        print(password_candidate)
        print(email)
        print('AAAAAAAAA')

        # Making a cursor to use the db
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                suc = "Você está logado."
                return render_template('login.html', msg=suc)
            else:
                er = "Login falhou."
                return render_template('login.html', error=er)

        else:
            er = "Email não encontrado."
            return render_template('login.html', error=er)

        cur.close()
    return render_template('login.html')


app.secret_key = 'super secret key'
if __name__ == '__main__':
    app.run(debug=True)
