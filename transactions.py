import pdfkit
from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session, logging
from mysqldb import mysql
from wrappers import is_logged_in
transactions_api = Blueprint('transactions_api', __name__)


@is_logged_in
@transactions_api.route('/transactions/')
def transactions():
    transactions = []

    cur = mysql.connection.cursor()
    cur.execute("SELECT id as donorid, wisherid, name as donorname, cpf as donorcpf, email as donoremail, wishername,wishercpf,wisheremail,marca,description,type from users JOIN (SELECT id as wisherid, name as wishername,cpf as wishercpf, email as wisheremail,donorid,marca,description,type from (SELECT wisherid,donorid,marca,description,type FROM transaction JOIN equipaments where transaction.equipid = equipaments.equipid) as transequips JOIN users where transequips.wisherid = users.id) as wishequips where wishequips.donorid = users.id")
    transactions = cur.fetchall()
    donated = []
    received = []
    for t in transactions:
        if t["donorid"] == session["userid"]:
            donated.append(t)
        if t["wisherid"] == session["userid"]:
            received.append(t)

    return render_template("transactions.html", donated=donated, received=received)


@is_logged_in
@transactions_api.route('/get_titulo', methods=['POST'])
def get_titulo():
    return redirect(url_for('transactions_api.transactions'))
