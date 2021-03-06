#importing HTTPServer to create a server instance, and BaseHTTPRequestHandler to handle request depending on the request
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#cgi to process input submitted through <form> or <isindex>
import cgi
#sqlalchemy setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#handler class to determine which code to execute(which out put ot show) based on the HTTP request sent(GET, POST, etc)
class webserverHandler(BaseHTTPRequestHandler):
	#if the request is a GET request this method will be executed
	#this also overrides the do_GET in the BaseHTTPRequestHander super class
	def do_GET(self):
		try:
			#if the path ends with 'hello' then this statement will execute
			if self.path.endswith("/hello"):
				#reponding by telling that there was a successfull GET request
				self.send_response(200)
				#responding by telling that the server is replying with text in the form of html
				self.send_header('Content-type', 'text/html')
				#sending a blank line and indicates the end of the header
				self.end_headers()
				#output string to return to the client
				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += """<form method = 'POST' enctype = 'multipart/form-data' action = '/hello'><h2> What
				would you like me to say?<h2><input name = 'message' type = 'text'> <input name = 'message'
				type = 'submit' value = 'Submit'></form>"""
				output += "</body></html>"
				#sending message back to the client
				self.wfile.write(output)
				#printing output to the terminal
				print(output)

			if self.path.endswith("/hola"):
				#reponding by telling that there was a successfull GET request
				self.send_response(200)
				#responding by telling that the server is replying with text in the form of html
				self.send_header('Content-type', 'text/html')
				#sending a blank line and indicates the end of the header
				self.end_headers()
				#output string to return to the client
				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += """<form method = 'POST' enctype = 'multipart/form-data' action = '/hello'><h2> What
				would you like me to say?<h2><input name = 'message' type = 'text'> <input name ='message'
				type = 'submit' value = 'Submit'></form>"""
				output += "</body></html>"
				#sending message back to the client
				self.wfile.write(output)
				#printing output to the terminal
				print(output)

			#handler to display the names of the restaurants in the database	
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				output = ""
				output += "<a href = '/restaurants/new'>Make a new Restaurant Here</a></br></br>"
				output += "<html><body>"
				restaurants = session.query(Restaurant).all()
				for restaurant in restaurants:
					output += restaurant.name + "\n</br>"
					output += "<a href = '/restaurants/%s/edit'>Edit</a></br>" % restaurant.id
					output += "<a href = '/restaurants/%s/delete'>Delete</a></br>"% restaurant.id
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
			
			if self.path.endswith("/edit"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one() 
				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h1>"
					output += myRestaurantQuery.name
					output += "</h1>"
					output += "<form method = 'POST' enctype = 'multipart/form-data' action = '/restaurants/%s/edit'>" % restaurantIDPath
					output += "<input name = 'newRestaurantName' type = 'text' placeholder = '%s'>"%myRestaurantQuery.name
					output += "<input type = 'submit' value = 'Rename'>"
					output += "</form>"
					output += "</body></html>"
					self.wfile.write(output)
			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = "<html><body>"
					output += "<h1>Are you sure you want to delete "
					output += myRestaurantQuery.name
					output += " ? </h1>"
					output += "<form method = 'POST' enctype = 'multipart/formr-data' action = '/restaurants/%s/delete'>"%restaurantIDPath
					output += "<input type = 'submit' value = 'Delete'>"
					output += "</form>"
					output += "</body></html>"
					self.wfile.write(output)

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1>Make a New Restaurant</h1>"
				output += "<form method = 'POST' enctype = 'multipart/form-data' action = '/restaurants/new'>"
				output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant name'>"
				output += "<input type = 'submit' value = 'Create'>"
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
		except IOError:
			#page not found error
			self.send_error(404, "File not Found %s" % self.path)
	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get("newRestaurantName")
					#create a new restaurant
					newRestaurant = Restaurant(name = messagecontent[0])
					session.add(newRestaurant)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get("newRestaurantName")
					restaurantIDPath = self.path.split("/")[2]
					myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
					if myRestaurantQuery != []:
						myRestaurantQuery.name = messagecontent[0]
						session.add(myRestaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
				if myRestaurantQuery != []:
					session.delete(myRestaurantQuery)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
			'''
			#responding ny telling that there was a successfull POST request
			self.send_response(301)
			#end header response
			self.end_headers()
			#parsing html form header into content type (ctype) and dictonary of parameters(pdict)
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			#checking if we received a form data
			if ctype == 'multipart/form-data':
				#collecting fields from the form
				fields = cgi.parse_multipart(self.rfile, pdict)
				#getting contenct from the field with the name = 'message' in the form
				messagecontent = fields.get('message')
			output = ""
			output += "<html><body>"
			output += "<h2>Okay, how about this: </h2>"
			output += "<h1>%s</h1>" % messagecontent[0]
			output += """<form method = 'POST' enctype = 'multipart/form-data' action = '/hello'><h2> What
			would you like me to say?<h2><input name = 'message' type = 'text'> <input name = 'message' 
			type = 'submit' value = 'Submit'></form>"""
			output += "</body></html>"
			#sending output to the client
			self.wfile.write(output)
			print(output)
			'''
		except:
			pass

#main method to instantiate the server and specify the port number
def main():
	try:
		port = 8080
		#creating server named server
		server = HTTPServer(('',port), webserverHandler)
		print("Web server running on port %s" %port)
		#running the server forever
		server.serve_forever()

	except KeyboardInterrupt:
		print("^C entered, stopping web server...")
		#stopping the server on KeyboardInterrupt
		server.socket.close()

#entry point for program to check if the this file is the main running file
if __name__ == '__main__':
	main()