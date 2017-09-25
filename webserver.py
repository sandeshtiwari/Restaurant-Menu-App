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
				output += "<html><body>"
				restaurants = session.query(Restaurant).all()
				for restaurant in restaurants:
					output += restaurant.name + "\n</br>"
					output += "<a href = '#'>Edit</a></br>"
					output += "<a href = '#'>Delete</a></br>"
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
		except IOError:
			#page not found error
			self.send_error(404, "File not Found %s" % self.path)
	def do_POST(self):
		try:
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