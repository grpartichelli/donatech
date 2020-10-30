from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql

donor_api = Blueprint('donor_api', __name__)
###############################################################
# DOAR


@donor_api.route("/doar", methods=['GET', 'POST'])
def doar():

    if request.method == 'POST':

        userid = session["userid"]
        tipo = request.form["type"]
        description = request.form["description"]
        marca = request.form["marca"]

        if "accept" in request.form:
            # Making a cursor to use the db
            cur = mysql.connection.cursor()

            cur.execute("INSERT INTO equipaments(userid, marca, description,type, visible,donated) VALUES(%s,%s,%s,%s,%s)",
                        (userid, marca, description, tipo, 0, 0))
            mysql.connection.commit()
            cur.close()
            flash(
                "Sua doação foi registrada com sucesso e será avaliada por um administrador.", "success")
            return redirect(url_for('dashboard_api.dashboard'))

        else:
            return render_template('doar.html', error="Você deve marcar a checkbox.")

    return render_template('doar.html')

####################################################################
