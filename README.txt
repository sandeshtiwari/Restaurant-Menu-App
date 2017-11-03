Restaurant Menu App
This App allows users to login using their Gmail account to create, delete or edit thier restaurants. This app also
allows users to add items to the restaurant they own. All the users can view all restaurants and menus for all the
restaurants even if they are not the ower of the restaurant.

Features of this application:
1) Users can view all the restaurants even if they are not signed up or logged in and view all the menus for the 
	restaurants
2) Users can log in with their existing Gmail account to add a new restaurant and edit it.
3) Users can also make new items, delete and edit only in the restaurant they created.

Software and other requirements
-Python 3, PostgreSQL, the psycopg2 library for python.
-Virtualbox with vagrant to run the database virtually on a linux machine
	- Virtual Box can be downloaded here - https://www.virtualbox.org/wiki/Downloads
	- Vagrant can be downloaded here - https://www.vagrantup.com/downloads.html
		-Windows users- grant network permissions to Vagrant or make firewall exception.
	-Download the VM configuration by going to https://github.com/udacity/fullstack-nanodegree-vm and forking and cloaning the repository
		-Change to this directory in your terminal(Git Bash for Windows) and run the following commands:-
			-vagrant up - this will download the linux OS and install it.
			-vagrant ssh- to get the virtual terminal for linux
			- cd <into the directory>
			- python database_setup.py
			- python lotsofmenus.py
		- To run the application run the following command
			-python finalproject.py
		- The app runs on port 5000: so visit the following url in your browser
			- http://localhost:5000
		- To vist the API Endpoints in the application, visit the following urls
			- list all restaurants
				- http://localhost:5000/restaurants/JSON
			- list all the menus of a given restaurant id
				- http://localhost:5000/<int:restaurant_id>/menu/JSON
			- list the details of a menu item from a given restaurant
				- http://localhost:5000/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON
		