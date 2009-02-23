#-*- coding: UTF-8 -*-
#
# Copyright 2009 Vee Satayamas
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import cgi
import sys
from parser import parse
from drawer import draw
from StringIO import StringIO

def statements_to_specs(statements):
    d = {'activities': []}
    for statement in statements:
        if statement['type'] != 'activity':
            d[statement['type']] = statement
        else:
            d['activities'].append(statement)
    return d
            

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-type'] = 'application/xhtml+xml'
        path = os.path.join(os.path.dirname(__file__), 'index.html');
        val = {'login_url': users.create_login_url(self.request.uri),
               'logout_url': users.create_logout_url(self.request.uri).replace("&", "&amp;"),
               'user': users.get_current_user()}
        self.response.out.write(template.render(path, val))

    def post(self):
        self.response.headers['Content-type'] = 'application/xhtml+xml'
        path = os.path.join(os.path.dirname(__file__), 'index.html');
        raw_specs = self.request.get('specs')
        statements = parse(raw_specs)
        specs = statements_to_specs(statements)
        sio = StringIO()
        d = draw(specs, sio)
        svg = sio.getvalue()
        val = {'foo': 12,
               'svg': svg, 
               'h': d['maxy'], 
               'w': d['maxx'],
               'login_url': users.create_login_url(self.request.uri)}
        self.response.out.write(template.render(path, val))

class LoginHandler(webapp.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url(self.request.uri))
        
def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
