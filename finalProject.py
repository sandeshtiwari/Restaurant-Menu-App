from flask import Flask, render_template, request, redirect, url_for
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
	print("outside")
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['name'])
		session.add(newRestaurant)
		session.commit()
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
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editRestaurant.html', restaurant = editRestaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	deleteRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == 'POST':
		session.delete(deleteRestaurant)
		session.commit()
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

@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenuItem(restaurant_id):
	return render_template('newmenuitem.html')

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenuItem(restaurant_id, menu_id):
	return render_template('editmenuitem.html', item = item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id, menu_id):
	return render_template('deletemenuitem.html', item = item)


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)