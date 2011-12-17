from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import os

class ManageFriends(webapp.RequestHandler):
    def get(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates/manage_friends.html')
        self.response.out.write(template.render(template_path, {}))
