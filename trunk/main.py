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
import os
import cgi
import sys
from parser import parse
from drawer import draw

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
        path = os.path.join(os.path.dirname(__file__), 'index.html');
        val = dict(bar='123')
        self.response.out.write(template.render(path, val))

class Timeline(webapp.RequestHandler):
    def post(self):
        raw_specs = self.request.get('specs')
        statements = parse(raw_specs)
        specs = statements_to_specs(statements)
        self.response.headers['Content-type'] = 'image/svg+xml'
        self.response.out.write("""<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="1024px" height="800px" 
     xmlns="http://www.w3.org/2000/svg" version="1.1">
        """)
        draw(specs, self.response.out)
        self.response.out.write("""</svg>""")

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/timeline', Timeline)],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
