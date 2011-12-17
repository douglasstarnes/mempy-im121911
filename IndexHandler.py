from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.ext.webapp import template

import os
import random
import datetime
import logging

from models import *

class IndexHandler(webapp.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        if current_user is None:
            # if there is no user logged in, redirect them to a login page
            template_values = {
                "login_url": users.create_login_url(self.request.uri)
            }
            template_path = os.path.join(os.path.dirname(__file__), 'templates/login.html')
            self.response.out.write(template.render(template_path, template_values))
        else:
            # get or create a user account
            imuser = self.get_imuser(current_user.nickname())
            # listen for invitations
            token = channel.create_channel(imuser.channel_id)
            channel_id = imuser.channel_id
            friends = imuser.friends
            online_friends = self.get_online_friends(friends)
            template_values = {
                "channel_id": channel_id,
                "online_friends": online_friends,
                "nickname": imuser.nickname,
                "token": token
            }
            template_path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
            self.response.out.write(template.render(template_path, template_values))

    def get_imuser(self, nickname):
        q = db.GqlQuery("select * from IMUser where nickname=:1", nickname)
        if q.count() > 0:
            imuser = q[0]
            imuser.logged_in = True 
            imuser.last_activity = datetime.datetime.now()

            imuser.put()

            return imuser
        else:
            imuser = IMUser()
            imuser.nickname = nickname
            imuser.channel_id = str(random.randint(0, 4000000000))
            imuser.logged_in = True
            imuser.last_activity = datetime.datetime.now()
            imuser.friends = [nickname]

            imuser.put()

            return imuser

    def get_online_friends(self, friends):
        friend_list = ",".join(["'%s'" % (friend) for friend in friends])
        gql = "select * from IMUser where nickname in (%s)" % (friend_list)
        q = db.GqlQuery(gql)
        current_time = datetime.datetime.now()
        online_friends = []
        for friend in q:
            delta = current_time - friend.last_activity
            if delta.seconds > 600:
                # automatically log out any user idle more than 10 minutes
                logging.info("logging out %s", friend.nickname)
                friend.logged_in = False
                friend.put()
                online_friends.append({"nickname": friend.nickname})
            else:
                online_friends.append({"nickname": friend.nickname, "logged_in": 1})

        return online_friends
