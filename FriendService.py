from protorpc import messages
from protorpc import remote
from protorpc.webapp import service_handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models import *

import logging

#input
class FriendServiceAction(messages.Message):
    action = messages.StringField(1, required=True)
    nickname = messages.StringFiel

#output
class FriendServiceActionResponse(messages.Message):
    error = messages.StringField(1, required=True)

class FriendService(remote.Service):
    # this method expects a FriendServiceAction and will return a FriendServiceActionResponse
    @remote.method(FriendServiceAction, FriendServiceActionResponse)
    # url of service will be /FriendService.manage_friends (see manage_friends.html)
    def manage_friends(self, request):
        # we must be logged in (creates a headache for testing)
        current_user = users.get_current_user()
        error = ""
        if current_user is not None:
            if request.action == "add":
                q = db.GqlQuery("select * from IMUser where nickname=:1", current_user.nickname())
                if q.count > 0:
                    record = q[0]
                    if request.nickname in record.friends:
                        error = "your friends list already contains %s" % request.nickname
                    else:
                        # apparently StringListProperty is immutable? :(
                        record.friends.append(request.nickname)
                        q[0].delete()
                        record.put()
                        error = "added %s" % (request.nickname)
            elif request.action == "remove":
                q = db.GqlQuery("select * from IMUser where nickname=:1", current_user.nickname())
                if q.count > 0:
                    try:
                        record = q[0]
                        record.friends.remove(request.nickname) # will raise ValueError if request.nickname is not in friends
                        q[0].delete()
                        record.put()
                        error = "removed %s" % (request.nickname)
                    except ValueError:
                        # trying to remove a value not in a list raises ValueError
                        error = "could not find %s in your friend list" % (request.nickname)
            else:
                pass
        else:
            logging.info(__file__ + ': no user logged in')
        
        #create and return the response
        fsar = FriendServiceActionResponse()
        fsar.error = error
        return fsar

application = webapp.WSGIApplication(
    service_handlers.service_mapping(
        [('/FriendService', FriendService)]
    ),
    debug=True
)

if __name__ == "__main__":
    run_wsgi_app(application)