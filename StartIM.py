from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.ext.webapp import template
from django.utils import simplejson

import datetime
import os
import logging

from models import *

class StartIM(webapp.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        sid = int(self.request.get("sid"))
        token = channel.create_channel(str(sid))
        archived_messages = db.GqlQuery("select * from IMMessage where im_session_id=:1 order by timestamp desc limit 10", sid)

        q = db.GqlQuery("select * from IMSession where im_session_id=:1", sid)
        if q.count() > 0:
            # joining a session
            chatters = q[0].users
            if not current_user.nickname() in chatters:
                pass
            else:
                initial_message = "%s has joined the IM session" % current_user.nickname()
                imuser = db.GqlQuery("select * from IMUser where nickname=:1", current_user.nickname())[0]
                token = channel.create_channel(imuser.channel_id)
        else:
            # creating a new session
            nickname = self.request.get("nickname")
            self.create_new_session(sid, current_user.nickname(), nickname, token)
            recipient = db.GqlQuery("select * from IMUser where nickname=:1", nickname)
            recipient_channel = recipient[0].channel_id
            logging.info("recipient_channel: %s" % (recipient_channel))
            message = {
                "host": current_user.nickname(),
                "sid": sid
            }
            # send invite
            channel.send_message(recipient_channel, simplejson.dumps(message))
            initial_message = "waiting for %s to join the IM session" % (nickname)

        # list comprhension FTW
        archives = [
            {
                "timestamp": msg.timestamp.strftime("%A, %B %d, %Y %H:%M:%S"),
                "author": msg.author,
                "message": msg.message
            }
            for msg in archived_messages
        ]

        template_path = os.path.join(os.path.dirname(__file__), 'templates/im.html')
        template_values = {
            "token": token,
            "archived_messages": archives,
            "initial_message": initial_message,
            "current_user": current_user.nickname(),
            "sid": sid
        }
        self.response.out.write(template.render(template_path, template_values))

    def create_new_session(self, sid, user1, user2, cid):
        im_session = IMSession()
        im_session.im_session_id = sid
        im_session.users = [user1, user2]
        im_session.last_activity = datetime.datetime.now()
        im_session.im_channel_token = cid

        im_session.put()

