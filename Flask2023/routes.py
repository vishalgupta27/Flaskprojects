import re

import bcrypt
import mysql.connector
from flask import session, redirect, request, url_for, render_template, flash
from werkzeug.utils import secure_filename
import os
import uuid

from Flask2023 import app

app.secret_key = "secret_key"

# Set the directory where uploaded images will be saved
UPLOAD_FOLDER = 'C:\\Users\\VISHAL-PC\\PycharmProjects\\myprojects\\Flask2023\\static\\uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}  # Define the allowed file extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Establish a connection to your MySQL database
mysql_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password',
    database='startup'
)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/page_sign', methods=['GET', 'POST'])
def page_sign():
    try:
        if 'loggedin' in session:
            return redirect(url_for('index'))
        if request.method == 'POST':
            print("inside post")
            username = request.form['username']
            password = request.form['password']
            print(username, "------", password)
            cursor = mysql_connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
            account = cursor.fetchone()
            print(account, '_____')
            print(bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')))
            if account and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('index'))  # Redirect to index on successful login
            else:
                msg = 'Incorrect username/password!'
                return render_template('logins.html', msg=msg)

        return render_template('logins.html')

    except Exception as e:
        print(e, "87777777777777777777777778")
        return render_template('logins.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('page_sign'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'address' in request.form and 'profile_image' in request.files:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        filename = None
        file = request.files['profile_image']
        if file.filename != '' and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = secure_filename(email.split('@')[0] + '_@profileimages')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor = mysql_connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                'INSERT INTO user (username, email, password, address, images) VALUES (%s, %s, %s, %s, %s)',
                (username, email, hashed_password, address, filename))
            mysql_connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


@app.route('/reset_password', methods=['Get', 'POST'])
def reset_password():
    if request.method == 'POST' and 'new_password' in request.form and 'confirm_password' in request.form and 'email' in request.form:
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']

        if new_password != confirm_password:
            msg = "Passwords do not match"
            return render_template('reset.html', msg=msg)
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor = mysql_connection.cursor(dictionary=True)
        cursor.execute('UPDATE user SET password = %s WHERE email = %s', (hashed_password, email))
        mysql_connection.commit()

        msg = "Password updated successfully"
        return render_template('logins.html', msg=msg)

    return render_template('reset.html')


@app.route('/index')
def index():
    if 'loggedin' in session:
        # Retrieve the user's email and profile image from the session or database
        username = session['username']

        # Query the database to retrieve the user's profile image filename
        cursor = mysql_connection.cursor()
        cursor.execute('SELECT images FROM user WHERE username = %s', (username,))
        result = cursor.fetchone()
        if result:
            images = result[0]
        else:
            images = None

        return render_template('index.html', images=images)
    return redirect(url_for('page_sign')),


@app.route('/success_update')
def success():
    if 'loggedin' in session:
        return render_template('successudapte.html')
    return redirect(url_for('page_sign'))


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if 'loggedin' not in session:
        return redirect(url_for('page_sign'))

    if request.method == 'POST':
        # Retrieve the updated user information from the form data
        username = request.form['username']
        email = request.form['email']
        address = request.form['address']

        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Update the user's profile image filename in the database
                cursor = mysql_connection.cursor()
                cursor.execute(
                    'UPDATE user SET username = %s, email = %s, address = %s, images = %s WHERE id = %s',
                    (username, email, address, filename, session['id']))
                mysql_connection.commit()
            else:
                # Update the user's information in the database without changing the profile image
                cursor = mysql_connection.cursor()
                cursor.execute('UPDATE user SET username = %s, email = %s, address = %s WHERE id = %s',
                               (username, email, address, session['id']))
                mysql_connection.commit()
        else:
            error_msg = 'Please upload a valid JPG image file.'
            return render_template('edit_user.html', error_msg=error_msg)
        # Redirect the user to a profile page or display a success message
        return redirect(url_for('success'))

    elif request.method == 'GET':
        # Fetch the current user's information from the database
        cursor = mysql_connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user WHERE id = %s', (session['id'],))
        user = cursor.fetchone()

        # Render the edit user form with the current user's information pre-filled
        return render_template('edit_user.html', user=user)
