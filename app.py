from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import pymysql.cursors
import re
import os
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super secret key'
app.config['MYSQL_HOST'] = 'containers-us-west-67.railway.app'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ucbqViOuL8XrvP9B4B6n'
app.config['MYSQL_DB'] = 'railway'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

def get_mysql_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@app.route('/')
def landing():
    if 'loggedin' in session:
        return redirect(url_for('post_login'))

    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM articles WHERE assigned = 0")
            data = cursor.fetchall()
        return render_template('index.html', data=data)
    finally:
        connection.close()

@app.route('/post_login', methods=['GET', 'POST'])
def post_login():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM articles WHERE assigned = 0 or assigned = %s ORDER BY assigned DESC",
                           (session['id'],))
            data = cursor.fetchall()
        return render_template('list.html', data=data, name=session['name'])
    finally:
        connection.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('post_login'))

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        connection = get_mysql_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM accounts WHERE email = %s or mobileNo = %s AND password = %s',
                               (username, username, password))
                account = cursor.fetchone()

            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['name'] = account['name']
                session.permanent = True  # Make the session permanent
                msg = 'Logged in successfully!'
                return redirect(url_for('post_login'))
            else:
                msg = 'Incorrect username / password!'
        finally:
            connection.close()

    return render_template('login.html', msg=msg)

# Remaining routes and code...

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
