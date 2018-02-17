# -*- coding: utf-8 -*-
import hashlib
import requests
from flask import Flask, render_template, session, request, redirect
# from flask_session import Session
import random
import json
import os
import time
os.environ['NO_PROXY'] = 'localhost'

APP_SECRET_KEY = 'blockchain'
APP_CONFIG_SESSION_TYPE = 'filesystem'
APP_DEBUG = True

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config['SESSION_TYPE'] = APP_CONFIG_SESSION_TYPE
app.debug = APP_DEBUG
config = {'is_org' : False}

# https://pythonspot.com/login-authentication-with-flask/

@app.route('/login', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    password = request.form['password']
    h = hashlib.sha1()
    h.update(password.encode('utf-8'))
    idenID = username + '$' + h.hexdigest()
    url = "http://localhost:3000/api/Identity_u/"+idenID
    r = requests.get(url)
    if r.status_code == 200:
        session['logged_in'] = True
        session['id'] = idenID
        if (r.json()['type'] == 'ORG'):
            config['is_org'] = True
    else:
        print('Wrong password!')
    return redirect_dest('/')

def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest)
    except:
        return redirect(fallback)
    return redirect(dest_url)


@app.route('/signup', methods=['POST'])
def do_admin_signup():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    type_of_user = request.form['type_of_user']
    email = request.form['email']
    dollar_class = 'org.acme.biznet.Identity_u'
    h = hashlib.sha1()
    h.update(password.encode('utf-8'))
    idenID = username + '$' + h.hexdigest()

    url = "http://localhost:3000/api/Identity_u"
    data = {
        'idenId': idenID,
        'name': name,
        'type': type_of_user,
        'email': email,
        '$class': 'org.acme.biznet.Identity_u'
    }
    headers = {'content-type': 'application/json'}
    # print (data)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print (r)
    if r.status_code == 200:
        session['logged_in'] = True
        session['id'] = idenID
        config['is_org'] = True
    return redirect_dest("/")


@app.route("/logout")
def logout():
    session['logged_in'] = False
    del session['id']
    print ('here in logout')
    return redirect_dest("/")


@app.route("/verify", methods=["POST"])
def verify():
    verified = "Verified"
    if request.form['remarks'] == '1':
        verified = "Wrong"
    data = {
      "$class": "org.acme.biznet.VerifyContract",
      "track": "resource:org.acme.biznet.Tracks#"+request.form['track_id'],
      "verify_remarks": request.form['remarks'],
      "isVerified": verified
    }
    url = "http://localhost:3000/api/VerifyContract"
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        print('done')
    else:
        print ('some error TODO')
    print (data)
    return redirect_dest('/tracks')

@app.route("/")
def main():
    # return render_template("dashboard.html")
    if session.get('logged_in', False):
        print ('sgjbjsdbvjsdbvj')
        return render_template('dashboard.html', session_id=session['id'])
    else:
        print ('skdjbv')
        return render_template('main.html')


@app.route("/create_track_submit", methods=["POST"])
def create_track_submit():
    print(request.form)
    h = hashlib.sha1()
    h.update(str(time.time()).encode('utf-8'))
    data = {
    'isVerified': 'Unverified',
    'verifier' :request.form['verifier'],
    'owner_id': session['id'],
    'description': request.form['job_desc'],
    'jobTitle': request.form['job_title'],
    'trackId': session['id'] + '$' + h.hexdigest(),
    '$class': 'org.acme.biznet.Tracks'
    }
    url = "http://localhost:3000/api/Tracks"
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        print('done')
    else:
        print ('some error TODO')
    return redirect_dest("/create")


@app.route("/create")
def create():
    url = "http://localhost:3000/api/Identity_u/"+session['id']
    r = requests.get(url)
    user_data = r.json()
    url = "http://localhost:3000/api/Identity_u/"
    r = requests.get(url)
    tot_data = r.json()
    org_list = []
    for row in tot_data:
        if(row['type'] == 'ORG'):
            org_list.append([row['name'], row['idenId']])
    data ={'user' : user_data['name'], 'email' : user_data['email'], 'org_list' : org_list, 'is_org':config['is_org']}
    return render_template("create-track.html", **data)




@app.route("/tracks")
def tracks():
    url = "http://localhost:3000/api/Tracks/"
    r = requests.get(url)
    tot_data = r.json()
    verified_list = []
    unverified_list = []
    if(config['is_org'] == True):
        for row in tot_data:
            if(row['verifier'] == session['id']):
                if(row['isVerified'] == 'Unverified'):
                    unverified_list.append(row)
                else:
                    verified_list.append(row)
    else:
        for row in tot_data:
            if(row['owner_id'] == session['id']):
                if(row['isVerified'] == 'Unverified'):
                    unverified_list.append(row)
                else:
                    verified_list.append(row)
    data = {'unverified':unverified_list , 'verified':verified_list, 'is_org':config['is_org']}
    print (tot_data, unverified_list, verified_list)
    return render_template("tracks.html", **data)


@app.route("/cv")
def cv():
    url = "http://localhost:3000/api/Tracks/"
    r = requests.get(url)
    tot_data = r.json()
    verified_list = []
    unverified_list = []
    if(config['is_org'] == True):
        for row in tot_data:
            if(row['verifier'] == session['id']):
                if(row['isVerified'] == 'Unverified'):
                    unverified_list.append(row)
                else:
                    verified_list.append(row)
    else:
        for row in tot_data:
            if(row['owner_id'] == session['id']):
                if(row['isVerified'] == 'Unverified'):
                    unverified_list.append(row)
                else:
                    verified_list.append(row)
    url = "http://localhost:3000/api/Identity_u/"+session['id']
    r = requests.get(url)
    data_user = r.json()
    data = {'unverified':unverified_list , 'verified':verified_list, 'is_org':config['is_org'], 'email':data_user['email'], 'name':data_user['name']}
    return render_template("cv.html", **data)

app.run(host='0.0.0.0', port=8081)
