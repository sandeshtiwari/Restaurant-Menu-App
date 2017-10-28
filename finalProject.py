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

#reading the json file for client id
CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/login/')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

@app.route('/gconnect/', methods = ['POST'])
def gconnect():
	print('in')
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

@app.route('/gdisconnect/')
def gdisconnect():
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
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/restaurants/JSON')
def resstaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return jsonify(MenuItems = [item.serialize for item in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def menuItemJSON(restaurant_id, menu_id):
	menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
	return jsonify(MenuItem = menuItem.serialize)

@app.route('/')
@app.route('/restaurants/', methods = ['GET', 'POST'])
def showRestaurants():
	restaurants = session.query(Restaurant)
	rows = session.query(Restaurant).count()
	if 'username' not in login_session:
		return render_template('publicrestaurants.html', restaurants = restaurants, rows = rows)
	return render_template('restaurants.html', restaurants = restaurants, rows = rows)

@app.route('/restaurant/new', methods = ['GET', 'POST'] )
def newRestaurant():
	if 'username' not in login_session:
		return redirect('/login/')
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['name'], user_id = login_session['user_id'])
		session.add(newRestaurant)
		session.commit()
		flash("New restaurant created!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login/')
	editRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if editRestaurant.user_id != login_session['user_id']:
		return "<script>function myFunction() { alert('You are not authorized');} </script><body onload = myFunction() ''>"
	if request.method == 'POST':
		if request.form['name']:
			editRestaurant.name = request.form['name']
		session.add(editRestaurant)
		session.commit()
		flash("Edited successfully!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editRestaurant.html', restaurant = editRestaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login/')
	deleteRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if deleteRestaurant.user_id != login_session['user_id']:
		return "<script>function myFunction() { alert('You are not authorized');} </script><body onload = myFunction() ''>"
	if request.method == 'POST':
		session.delete(deleteRestaurant)
		session.commit()
		flash("Deleted successfully!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('deleteRestaurant.html', restaurant = deleteRestaurant)

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	rows = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).count()
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	creator = getUserInfo(restaurant.user_id)
	if 'username' not in login_session or creator.id != login_session['user_id']:
		return render_template('publicmenu.html', items = items, restaurant = restaurant, rows = rows)
	return render_template('menu.html', restaurant= restaurant, items = items, rows = rows, creator = creator)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login/')
	Restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if Restaurant.user_id != login_session['user_id']:
		return "<script>function myFunction() { alert('You are not authorized');} </script><body onload = myFunction() ''>"
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

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	if 'username' not in login_session:
		return redirect('/login/')
	editMenuItem = session.query(MenuItem).filter_by(id = menu_id).one()
	Restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if Restaurant.user_id != login_session['user_id']:
		return "<script>function myFunction() { alert('You are not authorized');} </script><body onload = myFunction() ''>"
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

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	if 'username' not in login_session:
		return redirect('/login/')
	Restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if Restaurant.user_id != login_session['user_id']:
		return "<script>function myFunction() { alert('You are not authorized');} </script><body onload = myFunction() ''>"
	deleteItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		session.delete(deleteItem)
		session.commit()
		flash("Deleted successfully!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html', item = deleteItem, restaurant_id = restaurant_id)

def getUserID(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

def getUserInfo(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	return user

def createUser(login_session):
	newUser = User(name = login_session['username'], email = login_session['email'],picture =
		login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)