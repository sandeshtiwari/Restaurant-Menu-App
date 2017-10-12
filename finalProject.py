from flask import Flask, render_template
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, newMenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
	return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurant/new')
def newRestaurant():
	return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
	return render_template('editRestaurant.html', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
	return render_template('deleteRestaurant.html', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	return render_template('menu.html', restaurant= restaurant, items = items)

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