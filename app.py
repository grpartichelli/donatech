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

    try:
        if session["logged_in"]:
            return redirect(url_for("dashboard"))
        else:
            return render_template('home.html')
    except:
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
                session['role'] = data['role']
                session['name'] = data['name']
                session['userid'] = data['id']

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
# WRAPPERS
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

# Check if user is admin logged_in


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session["role"] == 'admin':
            return f(*args, **kwargs)
        else:
            flash("Somente Administradores podem acessar essa área", "danger")
            return redirect(url_for("/dashboard"))
    return wrap


####################################################################
# DASHBOARD


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

####################################################################
# ADMIN


@app.route('/admin')
@is_admin
def admin():
    # Making a cursor to use the db
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipaments;")
    data = cur.fetchall()
    cur.close()

    return render_template('admin.html', data=data)


@app.route('/toggle_visible/<equipid>/<visible>', methods=['POST'])
def toggle_visible(equipid, visible):
    # Making a cursor to change the db
    cur = mysql.connection.cursor()

    if visible == "1":
        v = 0
    else:
        v = 1
    cur.execute(
        "UPDATE equipaments SET visible = %s  WHERE equipid = %s", (v, equipid))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin'))

#################################
# LOGOUT


@app.route("/logout")
def logout():
    session.clear()
    flash("Você está deslogado", "success")
    session["logged_in"] = False
    return redirect(url_for('login'))

####################################################
# DOAR


@app.route("/doar", methods=['GET', 'POST'])
def doar():

    if request.method == 'POST':

        userid = session["userid"]
        tipo = request.form["type"]
        description = request.form["description"]
        marca = request.form["marca"]

        if "accept" in request.form:
            # Making a cursor to use the db
            cur = mysql.connection.cursor()
            # cur.execute("SELECT * FROM users WHERE email = lol")
            cur.execute("INSERT INTO equipaments(userid, marca, description,type, visible) VALUES(%s,%s,%s,%s,%s)",
                        (userid, marca, description, tipo, 0))
            mysql.connection.commit()
            cur.close()
            flash(
                "Sua doação foi registrada com sucesso e será avaliada por um administrador.", "success")
            return redirect(url_for('dashboard'))

        else:
            return render_template('doar.html', error="Você deve marcar a checkbox.")

    return render_template('doar.html')

####################################################################

# PROCURAR ITEMS


@app.route("/procuraritems", methods=['GET', 'POST'])
def procuraritems():

    # Making a cursor to use the db
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipaments where visible = 1")
    equips = cur.fetchall()

    # remove items on the users wishlist
    cur.execute("SELECT * FROM wishlist where userid = %s",
                (session["userid"],))
    wishlist = cur.fetchall()
    cur.close()

    nonwishlistequips = []
    # probably overcomplicated im tired
    for e in equips:
        flag = True
        for w in wishlist:
            if e["equipid"] == w["equipid"]:
                flag = False

        if flag:
            nonwishlistequips.append(e)
    data = nonwishlistequips

    # If user made a search
    if request.method == "POST":
        # search for the correct equipments
        if request.form["equiptype"] != "Mostrar Todos" and request.form["equiptype"] != "Equipamento...":
            data = []
            for e in nonwishlistequips:
                if e["type"] == request.form["equiptype"]:
                    data.append(e)

    return render_template("procuraritems.html", data=data)


@app.route('/add_to_wishlist/<equipid>', methods=['POST'])
def add_to_wishlist(equipid):
    # Making a cursor to change the db
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO wishlist(equipid,userid) VALUES(%s,%s)",
                (equipid, session["userid"]))
    mysql.connection.commit()
    cur.close()
    flash("Item adicionado com sucesso", "success")
    return redirect(url_for('procuraritems'))


############################################
app.secret_key = 'super secret key'
if __name__ == '__main__':
    app.run(debug=True)
