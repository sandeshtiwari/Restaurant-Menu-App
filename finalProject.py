from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()



@app.route('/')
@app.route('/restaurants', methods = ['GET', 'POST'])
def showRestaurants():
	restaurants = session.query(Restaurant)
	rows = session.query(Restaurant).count()
	return render_template('restaurants.html', restaurants = restaurants, rows = rows)

@app.route('/restaurant/new', methods = ['GET', 'POST'] )
def newRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['name'])
		session.add(newRestaurant)
		session.commit()
		flash("New restaurant created!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
	editRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
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
	deleteRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
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
	return render_template('menu.html', restaurant= restaurant, items = items, rows = rows)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		price = '$' + str(request.form['price'])
		newMenuItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id, course = request.form['course'], description = request.form['description'], price = price)
		session.add(newMenuItem)
		session.commit()
		flash("Created new item successfully!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	editMenuItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editMenuItem.name = request.form['name']
		session.add(editMenuItem)
		session.commit()
		flash("Edited Successfully!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('editmenuitem.html', item = editMenuItem, restaurant_id = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	deleteItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		session.delete(deleteItem)
		session.commit()
		flash("Deleted successfully!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html', item = deleteItem, restaurant_id = restaurant_id)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)