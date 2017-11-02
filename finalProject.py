# importing flask and other modules
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as login_session
import random, string
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# reading the json file for client id
CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()
# route for the login page
@app.route('/login/')
def showLogin():
	# state to handle cross site forgery attack
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)
# route to connect to the users gmail account
@app.route('/gconnect/', methods = ['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	code = request.data
	try:
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	#check that the access token is valid
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	#if there was an erro in the access token info, abort
	if result.get('error') is not None:
		response = make_response(json.dumps(reslut.get('error')), 50)
		response_headers['Content-Type'] = 'application/json'
	#verify that the access token is used for the intended user
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	#check to see if user is already logged in
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected'), 200)
		response.headers['Content-Type'] = 'application/json'
	#store the accesss token in the session for later use.
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	#get user info from google
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)
	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']
	user_id = getUserID(login_session['email'])
	if not user_id:
		print("I'm here")
		user_id = createUser(login_session)
	login_session['user_id'] = user_id
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output
# route to disconnect or logout the user from their account
@app.route('/gdisconnect/')
def gdisconnect():
	# getting the access token from the logged in user
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    # if the status of the response is error free
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showRestaurants'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showRestaurants'))
# route to display the resturants as JSON
@app.route('/restaurants/JSON')
def resstaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])
# route to show Menu of a restaurant as JSON
@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return jsonify(MenuItems = [item.serialize for item in items])
# route for displaying JSON for a particular menu item
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def menuItemJSON(restaurant_id, menu_id):
	menuItem = session.query(MenuItem).filter_by(id = menu_id, restaurant_id = restaurant_id).one()
	return jsonify(MenuItem = menuItem.serialize)
# route to display the restaurants
@app.route('/')
@app.route('/restaurants/', methods = ['GET', 'POST'])
def showRestaurants():
	restaurants = session.query(Restaurant)
	rows = session.query(Restaurant).count()
	# checking which menu to display based on the user login status
	if 'username' not in login_session:
		print('here')
		return render_template('publicrestaurants.html', restaurants = restaurants, rows = rows)
	return render_template('restaurants.html', restaurants = restaurants, rows = rows, user = login_session['user_id'])
# route for adding new restaurant
@app.route('/restaurant/new', methods = ['GET', 'POST'] )
def newRestaurant():
	# checking if the user is logged in
	if 'username' not in login_session:
		flash("Please login to continue")
		return redirect(url_for('showLogin'))
	# if a POST request is sent, then adding the restaurant to the database
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['name'], user_id = login_session['user_id'])
		session.add(newRestaurant)
		session.commit()
		flash("New restaurant created!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newRestaurant.html')
# route to edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
	# checking if the user is logged in
	if 'username' not in login_session:
		flash("Please login to continue")
		return redirect(url_for('showLogin'))
	editRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	# checking if the user is authorized to edit the restaurant
	if editRestaurant.user_id != login_session['user_id']:
		flash("Not authorized!")
		return redirect(url_for('showRestaurants'))
	# if the request is POST, then editing the restaurant
	if request.method == 'POST':
		if request.form['name']:
			editRestaurant.name = request.form['name']
		session.add(editRestaurant)
		session.commit()
		flash("Edited successfully!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editRestaurant.html', restaurant = editRestaurant)
# route for deleting a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	# checking if the user is logged in
	if 'username' not in login_session:
		flash("Please login to continue")
		return redirect(url_for('showLogin'))
	deleteRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	# checking if the user is authorized to delete the restaurant
	if deleteRestaurant.user_id != login_session['user_id']:
		flash('Not authorized!')
		return redirect(url_for('showRestaurants'))
	# deleting the restaurant if the request is POST
	if request.method == 'POST':
		session.delete(deleteRestaurant)
		session.commit()
		flash("Deleted successfully!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('deleteRestaurant.html', restaurant = deleteRestaurant)
# routes to show menu of a restaurant
@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	rows = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).count()
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	creator = getUserInfo(restaurant.user_id)
	# displaying the menu based on if the user is logged in
	if 'username' not in login_session:
		return render_template('publicmenu.html', items = items, restaurant = restaurant, rows = rows)
	return render_template('menu.html', restaurant= restaurant, items = items, rows = rows, user = login_session['user_id'])
# route to add new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
	# checking if the user is logged in
	if 'username' not in login_session:
		flash("Please login to continue")
		return redirect(url_for('showLogin'))
	newRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	# checking if the user is authorized
	if newRestaurant.user_id != login_session['user_id']:
		flash("Not authorized!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	# if the method is POST, then add new menu item to the restaurant
	if request.method == 'POST':
		price = '$' + str(request.form['price'])
		newMenuItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id, course = request.form['course'],
		 description = request.form['description'], price = price, user_id = login_session['user_id'])
		session.add(newMenuItem)
		session.commit()
		flash("Created new item successfully!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id = restaurant_id)
# route to edit menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	creator = getUserInfo(restaurant.user_id)
	if 'username' not in login_session:
		flash("Please login to continue")
		return redirect(url_for('showLogin'))
	# checking if the user logged in is authorized
	elif creator.id != login_session['user_id']:
		flash("Not authorized")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	editMenuItem = session.query(MenuItem).filter_by(id = menu_id).one()
	# checking if the request is POST to make changes to the database
	if request.method == 'POST':
		if request.form['name']:
			editMenuItem.name = request.form['name']
		if request.form['price']:
			editMenuItem.price = '$' + str(request.form['price'])
		if request.form['description']:
			editMenuItem.description = request.form['description']
		session.add(editMenuItem)
		session.commit()
		flash("Edited Successfully!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('editmenuitem.html', item = editMenuItem, restaurant_id = restaurant_id)
# route to delete menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	creator = getUserInfo(restaurant.user_id)
	if 'username' not in login_session:
		flash("Please login to continue")
		return redirect(url_for('showLogin'))
	# checking if the user logged in is authorized
	elif creator.id != login_session['user_id']:
		flash("Not authorized")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	deleteItem = session.query(MenuItem).filter_by(id = menu_id).one()
	# making chages to the database if the method is POST
	if request.method == 'POST':
		session.delete(deleteItem)
		session.commit()
		flash("Deleted successfully!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html', item = deleteItem, restaurant_id = restaurant_id)
# function to get the user id for a given email
def getUserID(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None
# function to get the user object based on a given user id
def getUserInfo(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	return user
# create a new user based on the login_session
def createUser(login_session):
	newUser = User(name = login_session['username'], email = login_session['email'],picture =
		login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id
# program starts here
if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)