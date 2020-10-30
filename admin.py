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
    cur.execute("SELECT * FROM equipaments where donated=0;")
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
# LISTA DE EQUIPAMENTOS DESEJADOS


@is_admin
@admin_api.route('/admin/transaction', methods=['POST', 'GET'])
def admin_transaction():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM (SELECT  userid as wisherid , equipid as wequipid FROM wishlist) as wishes JOIN (SELECT equipid , userid as donatorid, marca, description, type from equipaments where donated=0) as equips WHERE equips.equipid = wishes.wequipid ORDER BY equipid;")
    data = cur.fetchall()

    # Para cada equipamento vamos separar uma lista de quem deseja ele
    equipments = []
    wishers = []
    for i in range(len(data)):
        d = data[i]
        wishers.append(d["wisherid"])

        if(i == len(data)-1 or d["equipid"] != data[i+1]["equipid"]):
            equipments.append({"equipid": d["equipid"], "donorid": d["donatorid"], "wishers": wishers, "num_of_wishers": str(len(wishers)),
                               "marca": d["marca"], "description": d["description"], "type": d["type"]})
            wishers = []

    return render_template("admin_transaction.html", data=equipments)

# PAGINA DE SELEÇÃO DE DONATARIO


@is_admin
@admin_api.route('/admin/transaction/select_donee/<data>/', methods=['POST', 'GET'])
def select_donee(data):
    data_dict = {}
    data_dict = ast.literal_eval(data)
    users = []
    for u in data_dict["wishers"]:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id,name,email,cpf FROM users WHERE id = %s", (u,))
        users.append(cur.fetchall()[0])
    print(users)
    return render_template("select_donee.html", data=data_dict, users=users)

# REALIZA A TRANSAÇÃO ADICIONANDO A TABELA


@is_admin
@admin_api.route('/admin/transaction/select_donee/do_transaction/<wisherid>/<donorid>/<equipid>/', methods=['POST', 'GET'])
def do_transaction(wisherid, donorid, equipid):
    print("DATA")
    print(wisherid, donorid, equipid)

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO transaction(wisherid,donorid,equipid) VALUES(%s,%s,%s)",
                (wisherid, donorid, equipid))

    cur.execute(
        "UPDATE equipaments SET donated = %s  WHERE equipid = %s", (1, equipid))

    mysql.connection.commit()
    cur.close()
    flash("Transição registrada! Os usuários envolvidos serão avisados.", "success")

    return redirect(url_for('admin_api.admin_transaction'))

# LISTA DE TRANSAÇÕES REALIZADAS


@is_admin
@admin_api.route('/admin/transaction/done')
def admin_transaction_done():
    data = []

    cur = mysql.connection.cursor()
    cur.execute("SELECT name as donorname, cpf as donorcpf, email as donoremail, wishername,wishercpf,wisheremail,marca,description,type from users JOIN (SELECT name as wishername,cpf as wishercpf, email as wisheremail,donorid,marca,description,type from (SELECT wisherid,donorid,marca,description,type FROM transaction JOIN equipaments where transaction.equipid = equipaments.equipid) as transequips JOIN users where transequips.wisherid = users.id) as wishequips where wishequips.donorid = users.id")
    data = cur.fetchall()

    return render_template("admin_transaction_done.html", data=data)
