from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, DepartmentName, EmployName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///colleges.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Department"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
tbs_cat = session.query(DepartmentName).all()


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    tbs_cat = session.query(DepartmentName).all()
    tbes = session.query(EmployName).all()
    return render_template('login.html',
                           STATE=state, tbs_cat=tbs_cat, tbes=tbes)
    # return render_template('myhome.html', STATE=state
    # tbs_cat=tbs_cat,tbes=tbes)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session
#####
# Home


@app.route('/')
@app.route('/home')
def home():
    tbs_cat = session.query(DepartmentName).all()
    return render_template('myhome.html', tbs_cat=tbs_cat)

#####
# Department hub for admins


@app.route('/DepartmentHub')
def DepartmentHub():
    try:
        if login_session['username']:
            name = login_session['username']
            tbs_cat = session.query(DepartmentName).all()
            tbs = session.query(DepartmentName).all()
            tbes = session.query(EmployName).all()
            return render_template('myhome.html', tbs_cat=tbs_cat,
                                   tbs=tbs, tbes=tbes, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing employs


@app.route('/DepartmentHub/<int:tbid>/AllDepartment')
def showDepartment(tbid):
    tbs_cat = session.query(DepartmentName).all()
    tbs = session.query(DepartmentName).filter_by(id=tbid).one()
    tbes = session.query(EmployName).filter_by(departmentnameid=tbid).all()
    try:
        if login_session['username']:
            return render_template('showDepartment.html', tbs_cat=tbs_cat,
                                   tbs=tbs, tbes=tbes,
                                   uname=login_session['username'])
    except:
        return render_template('showDepartment.html',
                               tbs_cat=tbs_cat, tbs=tbs, tbes=tbes)

#####
# Add New Employ


@app.route('/DepartmentHub/addDepartmentName', methods=['POST', 'GET'])
def addDepartmentName():
    '''add the new employ'''
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        departmentname = DepartmentName(name=request.form['name'],
                                        user_id=login_session['user_id'])
        session.add(departmentname)
        session.commit()
        return redirect(url_for('DepartmentHub'))
    else:
        return render_template('addDepartmentName.html', tbs_cat=tbs_cat)

########
# Edit Department name


@app.route('/DepartmentHub/<int:tbid>/edit', methods=['POST', 'GET'])
def editDepartmentName(tbid):
    '''edit the department name'''
    editDepartmentName = session.query(DepartmentName).filter_by(id=tbid).one()
    creator = getUserInfo(editDepartmentName.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this DepartmentName."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('DepartmentHub'))
    if request.method == "POST":
        if request.form['name']:
            editDepartmentName.name = request.form['name']
        session.add(editDepartmentName)
        session.commit()
        flash("editDepartmentName Edited Successfully")
        return redirect(url_for('DepartmentHub'))
    else:
        # tbs_cat is global variable we can them in entire application
        return render_template('editDepartmentName.html',
                               tb=editDepartmentName, tbs_cat=tbs_cat)

######
# Delete DepartmentName


@app.route('/DepartmentHub/<int:tbid>/delete', methods=['POST', 'GET'])
def deleteDepartmentName(tbid):
    '''delete the department name'''
    tb = session.query(DepartmentName).filter_by(id=tbid).one()
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Department name."
              "This  belongs to %s" % creator.name)
        return redirect(url_for('DepartmentHub'))
    if request.method == "POST":
        session.delete(tb)
        session.commit()
        flash("DepartmentName Deleted Successfully")
        return redirect(url_for('DepartmentHub'))
    else:
        return render_template('deleteDepartmentName.html',
                               tb=tb, tbs_cat=tbs_cat)

######
# Add New Department Name Details


@app.route('/DepartmentHub/addDepartmentName/addDepartmentEmployDetails/'
           '<string:tbname>/add', methods=['GET', 'POST'])
def addDepartmentEmployDetails(tbname):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    tbs = session.query(DepartmentName).filter_by(name=tbname).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tbs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Employ"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showDepartment', tbid=tbs.id))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        salary = request.form['salary']
        feedback = request.form['feedback']
        employdetails = EmployName(name=name, description=description,
                                   salary=salary,
                                   feedback=feedback,
                                   date=datetime.datetime.now(),
                                   departmentnameid=tbs.id,
                                   user_id=login_session['user_id'])
        session.add(employdetails)
        session.commit()
        return redirect(url_for('showDepartment', tbid=tbs.id))
    else:
        return render_template('addDepartmentEmployDetails.html',
                               tbname=tbs.name, tbs_cat=tbs_cat)

######
# Edit Department Employ details


@app.route('/DepartmentHub/<int:tbid>/<string:tbename>/edit',
           methods=['GET', 'POST'])
def editDepartmentEmploy(tbid, tbename):
    tb = session.query(DepartmentName).filter_by(id=tbid).one()
    employdetails = session.query(EmployName).filter_by(name=tbename).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this Item edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showDepartment', tbid=tb.id))
    # POST methods
    if request.method == 'POST':
        employdetails.name = request.form['name']
        employdetails.description = request.form['description']
        employdetails.price = request.form['salary']
        employdetails.feedback = request.form['feedback']
        employdetails.date = datetime.datetime.now()
        session.add(employdetails)
        session.commit()
        flash("Employ Edited Successfully")
        return redirect(url_for('showDepartment', tbid=tbid))
    else:
        return render_template('editDepartmentEmploy.html',
                               tbid=tbid,
                               employdetails=employdetails, tbs_cat=tbs_cat)

#####
# Delte Restaurent item


@app.route('/DepartmentHub/<int:tbid>/<string:tbename>/delete',
           methods=['GET', 'POST'])
def deleteDepartmentEmploy(tbid, tbename):
    tb = session.query(DepartmentName).filter_by(id=tbid).one()
    employdetails = session.query(EmployName).filter_by(name=tbename).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this as "
              "This  belongs to %s" % creator.name)
        return redirect(url_for('showDepartment', tbid=tb.id))
    if request.method == "POST":
        session.delete(employdetails)
        session.commit()
        flash("Deleted Department Employ Successfully")
        return redirect(url_for('showDepartment', tbid=tbid))
    else:
        return render_template('deleteDepartmentEmploy.html',
                               tbid=tbid,
                               employdetails=employdetails, tbs_cat=tbs_cat)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'}
                  )[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected user..'
                                            ), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json


@app.route('/DepartmentHub/JSON')
def allDepartmentJSON():
    departmentnames = session.query(DepartmentName).all()
    category_dict = [c.serialize for c in departmentnames]
    for c in range(len(category_dict)):
        departmentemploynames = [i.serialize for i in session.query(
                 EmployName).filter_by(
                     departmentnamesid=category_dict[c]["id"]).all()]
        if departmentemploynames:
            category_dict[c]["department"] = department
    return jsonify(DepartmentName=category_dict)

####


@app.route('/DepartmentHub/departmentName/JSON')
def categoriesJSON():
    ''' Shows the list of departments '''
    department = session.query(DepartmentName).all()
    return jsonify(departmentName=[c.serialize for c in department])

####


@app.route('/DepartmentHub/department/JSON')
def employJSON():
    '''shows the list of employees'''
    employ = session.query(EmployName).all()
    return jsonify(department=[i.serialize for i in employ])

#####


@app.route('/DepartmentHub/<path:department_name>/department/JSON')
def categoryEmployJSON(department_name):
    departmentName = session.query(DepartmentName).filter_by(
        name=department_name).one()
    department = session.query(EmployName).filter_by(
        departmentname=departmentName).all()
    return jsonify(departmentName=[i.serialize for i in department])

#####


@app.route('/DepartmentHub/<path:departmentname>/'
           '<path:employdetails_name>/JSON')
def DetailsJSON(departmentname, employdetails_name):
    departmentName = session.query(DepartmentName).filter_by(
        name=departmentname).one()
    employDetailsName = session.query(EmployName).filter_by(
           name=employdetails_name, departmentname=departmentName).one()
    return jsonify(employDetailsName=[employDetailsName.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8086)
