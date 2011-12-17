from google.appengine.ext import db

class IMUser(db.Model):
    nickname = db.StringProperty()
    channel_id = db.StringProperty()
    friends = db.StringListProperty()
    last_activity = db.DateTimeProperty()
    logged_in = db.BooleanProperty(default=False)

class IMMessage(db.Model):
    message_id = db.StringProperty()
    author = db.StringProperty()
    message = db.TextProperty()
    reply_to = db.StringProperty(default=None)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    im_session_id = db.IntegerProperty()

class IMSession(db.Model):
    im_session_id = db.IntegerProperty()
    users = db.StringListProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    last_activity = db.DateTimeProperty()
    im_channel_token = db.StringProperty()