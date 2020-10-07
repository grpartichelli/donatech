from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql
from wrappers import is_admin

admin_api = Blueprint('admin_api', __name__)
####################################################################
# ADMIN


@admin_api.route('/admin', methods=['POST', 'GET'])
@is_admin
def admin():
    # Making a cursor to use the db
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipaments;")
    data = cur.fetchall()
    cur.close()
    equips = data
    # If user made a search
    if request.method == "POST":
        # search for the correct equipments
        if "equiptype" in request.form and request.form["equiptype"] != "Mostrar Todos" and request.form["equiptype"] != "Equipamento...":
            data = []
            for e in equips:
                if e["type"] == request.form["equiptype"]:
                    data.append(e)

        if "visibility" in request.form and request.form["visibility"] != "Mostrar Todos":
            data = []
            for e in equips:
                if request.form["visibility"] == "Visiveis":
                    visible = 1
                else:
                    visible = 0
                if e["visible"] == visible:
                    data.append(e)

    return render_template('admin.html', data=data)


@is_admin
@admin_api.route('/toggle_visible/<equipid>/<visible>', methods=['POST'])
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
    return redirect(url_for('admin_api.admin'))


@is_admin
@admin_api.route('/delete_equip/<equipid>/', methods=['POST'])
def delete_equip(equipid):
    # Making a cursor to change the db
    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE from equipaments where equipid = %s", (equipid))
    mysql.connection.commit()
    cur.close()
    flash("Equipamento foi deletado.", "success")
    return redirect(url_for('admin_api.admin'))

#################################
