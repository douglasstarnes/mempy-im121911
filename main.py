from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from IndexHandler import IndexHandler
from ManageFriends import ManageFriends
from StartIM import StartIM
from NewMessage import NewMessage
from LogoutCron import LogoutCron
from LogoutWorker import LogoutWorker

application = webapp.WSGIApplication([
    ("/", IndexHandler),
    ("/manage_friends", ManageFriends),
    ("/begin_im", StartIM),
    ("/new_message", NewMessage),
    ("/logout_cron", LogoutCron),
    ("/logout_worker", LogoutWorker)
], debug=True)

if __name__ == "__main__":
    run_wsgi_app(application)