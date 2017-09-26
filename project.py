from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()
#route to the root directory
@app.route('/')
@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by( id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
	output = ""
	for item in items:
		output += item.name + "</br>"
		output += item.price + "</br>"
		output += item.description + "</br>"
		output += '</br></br>'
	return output

@app.route('/restaurant/<int:restaurant_id>/new')
def newMenuItem(restaurant_id):
	return "Page to create a new menu item."

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit')
def editMenuItem(restaurant_id, menu_id):
	return "Page to edit a menu item"

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id, menu_id):
	return "Page to delete a menu item"

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)