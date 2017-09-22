#importing HTTPServer to create a server instance, and BaseHTTPRequestHandler to handle request depending on the request
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

#handler class to determine which code to execute(which out put ot show) based on the HTTP request sent(GET, POST, etc)
class webserverHandler(BaseHTTPRequestHandler):
	#if the request is a GET request this method will be executed
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
				output += "<html><body>Hello!</body></html>"
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
				output += "<html><body>&#Hola!</body></html> <a herf='/hello'> Back to Hello </a>"
				#sending message back to the client
				self.wfile.write(output)
				#printing output to the terminal
				print(output)
		except IOError:
			#page not found error
			self.send_error(404, "File not Found %s" % self.path)


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