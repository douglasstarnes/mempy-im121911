# this is the background worker that actually changes the status of users who have been active more than ten minutes
from google.appengine.ext import webapp
from google.appengine.ext import db

import datetime
import logging

class LogoutWorker(webapp.RequestHandler):
    def post(self):
        current_time = datetime.datetime.now()
        active_imusers = db.GqlQuery("select * from IMUser where logged_in=True")
        for imuser in active_imusers:
            delta = current_time - imuser.last_activity
            if delta.seconds > 600:
                logging.info("automatically logged out user: %s" % (imuser.nickname))
                imuser.logged_in = False
                imuser.put()