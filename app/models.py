from app import db, weibo,app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin
import re
import sys
if sys.version_info >= (3,0):
    enable_serch = False
else:
    enable_serch = False #forbidden
    import flask.ext.whooshalchemy as whooshalchemy


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    avatarimg = db.Column(db.String(120), nullable=True)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id) # python2

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def avatar(self):
        if self.avatarimg == None:
            resp = weibo.get('users/show.json', {'uid':self.social_id})
            self.avatarimg = resp.data['avatar_hd']
            return self.avatarimg
        return self.avatarimg

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() >0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id
        )).filter(followers.c.follower_id == self.id).order_by(
        Post.timestamp.desc())

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', "", nickname)

class Post(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post %r>' % (self.body)

if enable_serch:
    whooshalchemy.whoosh_index(app, Post)
