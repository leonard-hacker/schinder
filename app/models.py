from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime

# many to many relation between topic and user
topics_user = db.Table('topics_user', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'))
)

# many to many relation between chat and user
chat_user = db.Table('chat_user', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'))
)

# many to many relation between user and user
matches = db.Table('matches', 
    db.Column('user_id_self', db.Integer, db.ForeignKey('user.id')),
    db.Column('user_id_jope', db.Integer, db.ForeignKey('user.id')),
)

class Safety_question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120), unique=True, nullable=False)

class User(UserMixin, db.Model):
    # req
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # roll can be a = Admin u = User p = Premium user
    # TODO: make this mean something
    roll = db.Column(db.String(10), unique=False, nullable=False)
    password_hash = db.Column(db.String(128))

    # saftey question and answer
    question_id = db.Column(db.Integer, db.ForeignKey('safety_question.id'))
    safety_answer = db.Column(db.String(10), unique=False)

    # profil
    discription = db.Column(db.String(256))
    # all (hate) topics of user
    topics = db.relationship(
        'Topic', secondary=topics_user,
        backref=db.backref('users', lazy='dynamic'))
    # all users that this user has joped
    joped =  db.relationship(
        'User', secondary=matches,
        primaryjoin=(matches.c.user_id_self == id),
        secondaryjoin=(matches.c.user_id_jope == id),
        backref=db.backref('joped_me', lazy='dynamic'), lazy='dynamic')
    # all chats this user is involved in
    chats = db.relationship(
        'Chat', secondary=chat_user,
        backref=db.backref('users', lazy='dynamic'))
    
    # (backref) joped_me


    def __repr__(self):
        return '<User %r>' % self.username

    # set password for user and save hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # display pofile pic of user in given size 
    def prof_pic(self, size):
        pic_src = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            pic_src, size)

db.Column(db.String(120), unique=True, nullable=False)
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=True)
    # (backref) users

    def __repr__(self):
        return '<Topic {}>'.format(self.name)

# chat is always between two usere 
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # (backref) users


class Msg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    msg_data = db.Column(db.String(256), nullable=False)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


