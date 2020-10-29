from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql
from wrappers import is_admin
import ast

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
    cur.execute(
        "DELETE from wishlist where equipid = %s", (equipid))
    mysql.connection.commit()
    cur.close()
    flash("Equipamento foi deletado.", "success")
    return redirect(url_for('admin_api.admin'))

################################# TRANSACTION #################


@is_admin
@admin_api.route('/admin/transaction', methods=['POST', 'GET'])
def admin_transaction():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM (SELECT  userid as wisherid , equipid as wequipid FROM wishlist) as wishes JOIN (SELECT equipid , userid as donatorid, marca, description, type from equipaments) as equips WHERE equips.equipid = wishes.wequipid ORDER BY equipid;")
    data = cur.fetchall()

    # Para cada equipamento vamos separar uma lista de quem deseja ele
    equipments = []
    wishers = []
    for i in range(len(data)):
        d = data[i]
        wishers.append(d["wisherid"])

        if(i == len(data)-1 or d["equipid"] != data[i+1]["equipid"]):
            equipments.append({"equipid": d["equipid"], "donatorid": d["donatorid"], "wishers": wishers, "num_of_wishers": str(len(wishers)),
                               "marca": d["marca"], "description": d["description"], "type": d["type"]})
            wishers = []

    return render_template("admin_transaction.html", data=equipments)


@is_admin
@admin_api.route('/admin/transaction/select_donee/<data>/', methods=['POST', 'GET'])
def select_donee(data):
    data_dict = {}
    data_dict = ast.literal_eval(data)
    print("DATA")
    print(data_dict)
    users = []
    for u in data_dict["wishers"]:
        cur = mysql.connection.cursor()
        cur.execute("SELECT name,email,cpf FROM users WHERE id = %s", (u,))
        users.append(cur.fetchall()[0])
    print(users)
    return render_template("select_donee.html", data=data_dict, users=users)
