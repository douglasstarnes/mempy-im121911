from google.appengine.ext import webapp
from google.appengine.api import channel
from django.utils import simplejson
from google.appengine.ext import db

from models import *

import uuid
import datetime
import logging

class NewMessage(webapp.RequestHandler):
    def post(self):
        #retrieve parameters
        new_message = self.request.get('new_message')
        author = self.request.get('author')
        sid = int(self.request.get('sid'))

        # store message
        im_message = IMMessage()
        im_message.im_session_id = sid
        im_message.message = new_message
        im_message.author = author
        im_message.message_id = str(uuid.uuid4())

        im_message.put()

        # update last_activity of sender to prevent automatic logout
        current_user = db.GqlQuery("select * from IMUser where nickname=:1", author)[0]
        current_user.last_activity = datetime.datetime.now()
        current_user.put()

        # get recipient list
        im_sessions = db.GqlQuery("select * from IMSession where im_session_id=:1", sid)[0]
        chatters = im_sessions.users

        # send message to all recipients
        for chatter in chatters:
            imuser = db.GqlQuery("select * from IMUser where nickname=:1", chatter)[0]
            logging.info(__file__ + " " + chatter)
            channel.send_message(imuser.channel_id, simplejson.dumps({
                "message": new_message,
                "author": author,
                "timestamp": datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S"),
            }))
