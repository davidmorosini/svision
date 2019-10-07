#
# s-handler source
#
#

from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
 
from core.webfunc import att_status, toggle_service

import sys
import logging

# This class contains methods to handle our requests to different URIs in the app
class Shandler(SimpleHTTPRequestHandler):
    def set_configs(self, configs):
        self.configs = configs

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
 
    # Check the URI of the request to serve the proper content.
    def do_GET(self):
        if('att' in self.path):
            self.respond(att_status())
        elif('service' in self.path):
            self.respond(toggle_service())
        else:
            super(Shandler, self).do_GET()

    def handle_http(self, data):
        self.send_response(200)
        # set the data type for the response header. In this case it will be json.
        # setting these headers is important for the browser to know what 	to do with
        # the response. Browsers can be very picky this way.
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        return bytes(data, 'UTF-8')
 
     # store response for delivery back to client. This is good to do so
     # the user has a way of knowing what the server's response was.
    def respond(self, data):
        response = self.handle_http(data)
        self.wfile.write(response)
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
            """Handle requests in a separate thread."""
