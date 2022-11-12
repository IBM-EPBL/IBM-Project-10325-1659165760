# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os, logging 

# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2              import TemplateNotFound

# App modules
from app        import app, lm, db, bc
from app.models import Users
from app.forms  import LoginForm, RegisterForm

import requests
from tensorflow.keras.models import load_model
from keras.preprocessing import image
import keras
import tensorflow as tf
import numpy as np
import json
from json import JSONEncoder
from ibm_watson_machine_learning import APIClient
import os


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

UPLOAD_FOLDER = "uploads"

@app.route('/classify', methods=['POST'])
def classify():
    if request.method == 'POST':
        file = request.files['fileupload']
        file_path = os.path.join(os.getcwd() + '/app/' + UPLOAD_FOLDER + '/' + file.filename)
        file.save(file_path)
        print(file_path)
        img = keras.utils.load_img(file_path, target_size=(64,64))
        x = tf.keras.utils.img_to_array(img)
        x = np.expand_dims(x, axis=0)

        numpyData = {"input_data": x}
        encodedNumpyData = json.dumps(numpyData, cls=NumpyArrayEncoder)

        API_KEY = os.environ["API_KEY"]
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

        payload_scoring = {
	        "input_data": [{
		    "fields": [],
		    "values": x.tolist()
	    }]
        }

        response_scoring = requests.post('https://eu-gb.ml.cloud.ibm.com/ml/v4/deployments/16df8175-8bb2-4ed2-9893-ac61d3349a89/predictions?version=2022-11-11', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
        res = response_scoring.json()['predictions'][0]['values'][0][0]
        count = 0
        pos = res.index(1.0)
        types = ['Left Bundle Branch Block', 'Normal', 'Premature Atrial Contraction', 'Premature Ventricular Contractions', 'Right Bundle Branch Block', 'Ventricular Fibrillation']
        current_user.addHistory(types[pos])
        hist = current_user.getHistory()
        return render_template('index.html', result = types[pos], history=hist)
    return render_template('index.html')

# provide login manager with load_user callback
# return User(u.name,u.id,u.active)
@lm.user_loader
def load_user(user_id):
    email, uname, passwd = Users.getUser(user_id)
    return Users(uname, email, passwd)

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    # declare the Registration Form
    form = RegisterForm(request.form)

    msg     = None
    success = False

    if request.method == 'GET': 

        return render_template( 'register.html', form=form, msg=msg )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        email    = request.form.get('email'   , '', type=str) 

        # filter User out of database through username
        user = Users.userExists(username)

        # filter User out of database through username
        user_by_email = Users.emailExists(email)

        if user or user_by_email:
            msg = 'Error: User exists!'
        
        else:         

            pw_hash = bc.generate_password_hash(password)

            user = Users(username, email, pw_hash)

            user.save()

            msg     = 'User created, please <a href="' + url_for('login') + '">login</a>'     
            success = True

    else:
        msg = 'Input error'     

    return render_template( 'register.html', form=form, msg=msg, success=success )

# Authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        # filter User out of database through username
        u = Users.getUserWithUname(username)
        user = Users(u[1], u[0], u[2])
        if user:
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template( 'login.html', form=form, msg=msg )

# App main route + generic routing
@app.route('/', defaults={'path': 'index'})
@app.route('/<path>')
def index(path):
    try:
        if current_user.is_authenticated:
            hist = current_user.getHistory()
            return render_template('index.html', history=hist)

        return render_template( 'index.html' )
    
    except TemplateNotFound:
        return render_template('index.html'), 404
    
    except:
        return render_template('index.html'), 500

# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')

