Restaurant Menu App
This App allows users to login using their Gmail account to create, delete or edit thier restaurants. This app also
allows users to add items to the restaurant they own. All the users can view all restaurants and menus for all the
restaurants even if they are not the ower of the restaurant.

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