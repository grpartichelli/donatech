from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql

donee_api = Blueprint('donee_api', __name__)

###############################################################################
# PROCURAR ITEMS


@donee_api.route("/procuraritems", methods=['GET', 'POST'])
def procuraritems():

    # Making a cursor to use the db
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM equipaments where visible = 1 and donated=0 and userid!=%s", (session["userid"],))
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

    return render_template("donee/procuraritems.html", data=data)


@ donee_api.route('/add_to_wishlist/<equipid>', methods=['POST'])
def add_to_wishlist(equipid):
    # Making a cursor to change the db
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO wishlist(equipid,userid) VALUES(%s,%s)",
                (equipid, session["userid"]))
    mysql.connection.commit()
    cur.close()
    flash("Item adicionado com sucesso", "success")
    return redirect(url_for('donee_api.procuraritems'))


@ donee_api.route('/wishlist', methods=['GET', 'POST'])
def wishlist():

    # Making a cursor to use the db
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM equipaments where visible = 1 and donated=0 and userid!=%s", (session["userid"],))
    equips = cur.fetchall()

    # remove items on the users wishlist
    cur.execute("SELECT * FROM wishlist where userid = %s",
                (session["userid"],))
    wishlist = cur.fetchall()
    cur.close()

    wishlistequips = []
    # probably overcomplicated im tired
    for e in equips:
        for w in wishlist:
            if e["equipid"] == w["equipid"]:
                wishlistequips.append(e)

    data = wishlistequips

    # If user made a search
    if request.method == "POST":
        # search for the correct equipments
        if request.form["equiptype"] != "Mostrar Todos" and request.form["equiptype"] != "Equipamento...":
            data = []
            for e in wishlistequips:
                if e["type"] == request.form["equiptype"]:
                    data.append(e)

    return render_template("donee/wishlist.html", data=data)
############################################
