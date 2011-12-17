# this is the helper that the cron scheduler calls which will spaw a background worker to do the actual work.
from google.appengine.ext import webapp
from google.appengine.api import taskqueue

class LogoutCron(webapp.RequestHandler):
    def get(self):
        taskqueue.add(url="/logout_worker")