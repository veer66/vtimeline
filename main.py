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
from google.appengine.ext import db
import os
import cgi
import sys
from StringIO import StringIO
from parser import parse
from drawer import draw
from utils import statements_to_specs
import model


class MainHandler(webapp.RequestHandler):
    def common_val(self):
        specs_list = model.Specs.all()
        specs_list.filter("author =", users.get_current_user())
        specs_list.order("-date")
        val = {'logout_url': users.create_logout_url(self.request.uri).replace("&", "&amp;"),
               'user': users.get_current_user(),
               'specs_list': specs_list}
        return val

    def get(self):
        user = users.get_current_user()
        if user:
            self.response.headers['Content-type'] = 'application/xhtml+xml'
            path = os.path.join(os.path.dirname(__file__), 'index.html');
            val = self.common_val()
            action = self.request.get('action')
            key = self.request.get('key')
            if action == "delete":
                specs = model.Specs.get(key)
                if specs.author == user:
                    specs.delete()
            elif action == "load":
                specs = model.Specs.get(key)
                if specs.author == user:
                    val['specs'] = specs.content
                    val['title'] = specs.title
            self.response.out.write(template.render(path, val))
        else:
            self.redirect(users.create_login_url(self.request.uri))
       
    def create_svg(self, val, raw_specs):
        statements = parse(raw_specs)
        specs = statements_to_specs(statements)
        sio = StringIO()
        d = draw(specs, sio)
        svg = sio.getvalue()
        val['svg'] = svg 
        val['h'] = d['maxy']
        val['w'] = d['maxx']

    def post(self):
        user = users.get_current_user()
        if user:
            self.response.headers['Content-type'] = 'application/xhtml+xml'
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            action = self.request.get('action')
            val = self.common_val()
            raw_specs = self.request.get('specs')
            if action == u"สร้างแผนภูมิ":
                # create diagram
                self.create_svg(val, raw_specs)
            else:
                # save specs
                specs = model.Specs()
                specs.content = raw_specs
                specs.title = self.request.get('title')
                specs.author = user
                specs.put()

            self.response.out.write(template.render(path, val))
        else:
            self.redirect(users.create_login_url(self.request.uri))

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
