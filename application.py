from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, db, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login/')
def showLogin():
    """
    Create an anti-forgery state token.

    Store state in the login session for validation.

    """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Handles Google+ Auth.

    Checks client and server state values. If the state values match update the
    authorization code into a credentials object, otherwise it returns an
    error.

    Obtains an access token for the user, and checks the token is valid, if so,
    the access token is stored in the session for later use, and the scope of
    the token i
    s then accessible.

    A query checks to see if the logged in user is in the database and if not
    adds the user to the database.


    """

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
                                'Failed to upgrade the authorization code.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Abort if there was an error in the access token info
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                                 "Token's user ID doesn't match given user ID."
                                 ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
                                 'Tokens client ID does not match apps'), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info allowed by token scope
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['email'] = data["email"]

    # Save user to database, if not already saved to database
    userInDB = session.query(User).filter_by("email= "
                                             "login_session['email']").all()
    if userInDB:
        output = ''
        output += '<h1>Welcome back, '
        output += login_session['username']
        output += '!</h1>'
        return output
    else:
        newUser = User(name=login_session['username'],
                       email=login_session['email'])
        session.add(newUser)
        session.commit()
        output = ''
        output += '<h1>Thanks for signing up, '
        output += login_session['username']
        output += '!</h1>'
        return output


@app.route('/logout/')
@app.route('/catalog/logout/')
def logout():
    """
    Realeases variables from login_session using pop() method.

    """
    login_session.pop('state', None)
    login_session.pop('username', None)
    login_session.pop('email', None)
    flash("Successfully logged out.")
    return redirect(url_for('index'))


@app.route('/catalog/JSON/')
def catalogJSON():
    """
    JSON API to view category menu.


    """

    category = session.query(Category).all()
    return jsonify(category=[c.serialize for c in category])


@app.route('/catalog/<int:category_id>/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
    """
    JSON API to view an items details.


    """

    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).all()
    return jsonify([i.serialize for i in item])


@app.route('/catalog/<int:category_id>/JSON/')
def categoryItem(category_id):
    """
    JSON API Endpoint to view all the items in a category.


    """

    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(category_id=category_id).one()
    return jsonify(item=item.serialize)


@app.route('/catalog/user/JSON/')
def userJSON():
    """
    JSON API Endpoint to view a list of all users.


    """

    users = session.query(User).all()
    return jsonify([u.serialize for u in users])


@app.route('/')
@app.route('/catalog/')
def index():
    """
    Home page with navigation, featured items, and user options.

    """

    homeNav = session.query(Category).all()
    featuredItems = session.query(Item).all()
    if 'username' in login_session:
        flash('Your currently logged in as: %s' % login_session['username'])
        return render_template('index_loggedin.html', homeNav=homeNav,
                               featuredItems=featuredItems)
    else:
        return render_template('index.html', homeNav=homeNav,
                               featuredItems=featuredItems)


@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def categoryItems(category_id):
    """
    Lists all items in the selected category.

    If user is logged in, user options will be displayed. If not, the login
    button is displayed.


    """

    catItNav = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).all()
    items = session.query(Item).filter_by(category_id=category_id).all()
    if 'username' not in login_session:
        return render_template('categoryitems.html', catItNav=catItNav,
                               category=category, items=items)
    else:
        return render_template('categoryitems_loggedin.html',
                               catItNav=catItNav, category=category,
                               items=items)


@app.route('/catalog/<int:category_id>/<int:item_id>/')
@app.route('/catalog/items/<int:item_id>/')
def showItem(category_id, item_id):
    """
    Displays details about the item selected.

    User options are displayed in the navigation if the user is logged in,
    otherwise the login button is displayed.


    """

    showItNav = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    author = session.query(User).filter_by(id=item.user_id).one()
    if 'username' not in login_session:
        return render_template('item.html', showItNav=showItNav, item=item,
                               author=author)
    else:
        return render_template('item_loggedin.html', showItNav=showItNav,
                               item=item, author=author)


# Add a new item to the catalog (logged in users only)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    """
    The option to add an item is available to logged in users.

    If a user is not logged in and tries to access the page manually, an error
    message will be displayed and they will be redirected to the login page.

    After a logged in user has successfully added a new item, a success message
    will display and they are redirected to the home page.


    """

    newItNav = session.query(Category).all()
    allUsers = session.query(User).filter_by("email= "
                                             "login_session['email']").all()
    if 'username' not in login_session:
        flash("You need to login to add items to the catalog")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        for a in allUsers:
            user_id = a.id
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_id=request.form['category'],
                           user_id=user_id)
            session.add(newItem)
            session.commit()
            flash("Successfully Added %s to the Catalog!" % newItem.name)
            return redirect(url_for('index'))
    else:
        return render_template('newItem.html', newItNav=newItNav)


# Displays items added by the logged in user, with links to edit and delete


@app.route('/catalog/youritems/')
def yourItems():
    """
    Option is available only when a user is logged in.

    Page displays items created by the logged in user. Each item has the option
    to edit or delete.


    """

    yourItNav = session.query(Category).all()
    allUsers = session.query(User).filter_by(
        email=login_session['email']).all()
    # Checks if user is logged in
    if 'username' not in login_session:
        flash("Please login!")
        return redirect(url_for('showLogin'))
    else:
        for a in allUsers:
            user_id = a.id
            author = session.query(User).filter_by(id=user_id).all()
            yourItem = session.query(Item).filter_by(user_id=a.id).all()
            return render_template('yourItems.html', yourItem=yourItem,
                                   author=author, yourItNav=yourItNav)


@app.route('/catalog/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """
    Displays a form to edit an item.

    Checks if the user is logged in, if not user is redirected to the login
    page.

    If user is logged in, checks the user is the creator of the selected item.
    If not, the user does not have auhtority to edit the item and an error
    message is returned.

    If user is the creator, checks all fields are filled in and the item is
    updated in the database.


    """

    allUsers = session.query(User).filter_by(
        email=login_session['email']).all()
    editItNav = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    editedItem = session.query(Item).filter_by(id=item_id).one()
    # Checks if user is logged in
    if 'username' not in login_session:
        flash("Please login!")
        return redirect(url_for('showLogin'))
    for a in allUsers:
        user_id = a.id
        currentUser = session.query(User).filter_by(id=user_id).one()
        # Checks the users ID matches the authors ID
        if currentUser.id != item.user_id:
            flash("You are not authorised to edit this item.")
            return redirect(url_for('index'))
        if request.method == 'POST':
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['category']:
                editedItem.category_id = request.form['category']
            session.add(editedItem)
            session.commit()
            flash("Item Successfully Updated!")
            return redirect(url_for('index'))
        else:
            return render_template('edititem.html', category_id=category_id,
                                   item_id=item_id, editItNav=editItNav,
                                   currentUser=currentUser, item=item,
                                   editedItem=editedItem)


@app.route('/catalog/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(item_id, category_id):
    """
    Checks user is logged in, if not user is rediected to the login page.

    Checks the logged in user is the creator of the item, if not an error
    message is returned.

    If user is the creator, user is asked to confirm they want to delete the
    item. If cancelled, the user is redirected to their items page. If
    confirmed the item is deleted from the database.


    """

    delItNav = session.query(Category).all()
    allUsers = session.query(User).filter_by(email="\ "
                                             "| login_session['email']").all()
    item = session.query(Item).filter_by(id=item_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    # Checks that the user is logged in
    if 'username' not in login_session:
        flash("Please login to access this page.")
        return redirect(url_for('showLogin'))
    for a in allUsers:
        user_id = a.id
        currentUser = session.query(User).filter_by(id=user_id).one()
        # Checks if the logged in users ID matches the items author ID
        if currentUser.id != item.user_id:
            flash("You are not authorised to delete this item!!")
            return redirect(url_for('index'))
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash("%s successfully deleted" % itemToDelete.name)
            return redirect(url_for('categoryItems', category_id=category_id))
        else:
            return render_template('deleteitem.html', category_id=category_id,
                                   item_id=item_id, itemToDelete=itemToDelete,
                                   delItNav=delItNav, currentUser=currentUser,
                                   item=item)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='13.239.17.236', port=2200)
