from sqlalchemy import create_engine

from app import app, db
from flask import render_template, flash, redirect, url_for, request, Response,  Flask, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from .forms import LoginForm, RegistrationForm, ProfilForm, MatchForm, MsgForm, SearchForm, PasswordForm, ResetPw, \
    SQLForm
from .models import User, Topic, Chat, Msg, Safety_question

import random

# index view 
# landing page
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    return render_template('index.html')


# login view
# login to schinder
@app.route('/login', methods=['GET', 'POST'])
def login():

    # redirect to home view if user is authenticated already
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    login_form = LoginForm()

    if login_form.validate_on_submit():

        # get instance of user
        user = User.query.filter_by(username=login_form.username.data).first()
        # redirect if usere dosen't exist
        if user is None or not user.check_password(login_form.password.data):
            flash('Flascher Username oder falsches Passwort')
            return redirect(url_for('login'))

        # login instance of user
        login_user(user)
        flash("Wilkommen zurück " + user.username + ".")

        # get next page if it or redirct to home view
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)

    return render_template('login.html', form = login_form)


# logout view
# logout of schinder
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# registration view
# register new Schinder user

@app.route('/register',  methods=['GET', 'POST'])
def register():

    # redirect to home if current user is loged in allready
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    reg_form = RegistrationForm()


    # create new user if form is valid and redirect to login page
    if reg_form.validate_on_submit():
        user = User(username=reg_form.username.data, email=reg_form.email.data, roll = reg_form.roll.data)
        question = Safety_question.query.filter_by(question=reg_form.safety_question.data).first()
        user.question_id = question.id
        user.safety_answer = reg_form.answer.data
        user.set_password(reg_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Yuuuhu das hat geklappt! Du bist jetzt Mitglied von Schinder.')
        return redirect(url_for('login'))

    return render_template('register.html', form=reg_form)


# home view
# display possible matches

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    match_form = MatchForm()
    possible_matches = []

    # iterate trough all topics of current user
    for topic in current_user.topics:

        # get all users that have that topic and remove current user
        possible = topic.users.all()
        possible.remove(current_user)

        # only add users that current user hase't allready joped
        for pos in possible:
            if pos not in current_user.joped:
                possible_matches.append(pos)

    # return no matches if there arent any
    if len(possible_matches) == 0:
        return render_template('home.html')

    # get a random user out of all possible matches to be directly displayed
    match = possible_matches[random.randint(0,len(possible_matches)-1)]

    return render_template('home.html', match=match, match_form = match_form)


# add match view
# is called when user jopes / nopes another user
# displays 'It's a MATCH!'

@app.route('/home/<jopeid>', methods=['GET', 'POST'])
def add_match(jopeid):
    match_form = MatchForm()
    msg_form = MsgForm()

    # If it's a match user can send a message
    if msg_form.validate_on_submit():

        # create new Chat between the two users
        # TODO: check if empty field counts as msg
        chat = Chat()
        chat.users.append(current_user)
        chat.users.append(User.query.filter_by(id=jopeid).first())

        # add msg to chat
        msg = Msg(chat=chat.id, user=current_user.id, msg_data=msg_form.msg.data)

        # update db
        db.session.add(chat)
        db.session.add(msg)
        db.session.commit()

        return redirect(url_for('home'))

    # is true if user joped other user
    if match_form.yes.data:
        # get instace of joped user return 404 if user dosent exist (can only happen if someone messes with the request..)
        joped = User.query.filter_by(id=jopeid).first_or_404()

        # add joped user to current user
        if joped not in current_user.joped:
            current_user.joped.append(joped)
            db.session.commit()

        # check if joped user joped the current user as well
        if current_user in joped.joped:
            # return with is_match flag as true
            # TODO: add and show amount of shared topics
            return render_template('home.html', match=joped, msg_form = msg_form, is_match = True)
        else:
            return redirect(url_for('home'))

    else:
        return redirect(url_for('home'))


# matches view
# display all matches

@app.route('/matches')
@login_required
def matches():
    matches = []

    # TODO: show shared topics
    # get all matches that current user has (match = both useres have joped each other)
    for joped in current_user.joped:
        if current_user in joped.joped:
            matches.append(joped)

    # display matches if they exist
    if len(matches) != 0:
        return render_template('matches.html', matches = matches)
    else:
        return render_template('matches.html')


# profile view
# display / edit user profiles
# could use names instead of id might be a lil bit more interesting
# could lave another comment to make this stand out a lil bit more

@app.route('/user/<userid>', methods=['GET', 'POST'])
@login_required
def user(userid):
    # get user instance or 404
    user = User.query.filter_by(id=userid).first_or_404()

    profil_form = ProfilForm()

    if profil_form.validate_on_submit():
        # update user discription
        if current_user.discription != profil_form.discription.data and profil_form.save.data:
            user = User.query.get(current_user.id)
            user.discription = profil_form.discription.data
            db.session.commit()
            flash("Deine Beschreibung wurde geupdated.")

        # update user topics
        if profil_form.topic_select and profil_form.add.data:
            topic = Topic.query.filter_by(name=profil_form.topic_select.data).first_or_404()

            if topic in current_user.topics:
                user.topics.remove(topic)
            else:
                user.topics.append(topic)

            db.session.commit()
            flash("Deine Hassthemen wurde geupdated.")


    # display current user discription
    profil_form.discription.data = user.discription

    return render_template('user.html', user=user, profil_form=profil_form)



# reset password with safety question

@app.route('/reset_pw', methods=['get', 'post'])
def reset_pw():

    form = ResetPw()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        question = Safety_question.query.filter_by(question = form.safety_question.data).first()
        if user and user.question_id == question.id and user.safety_answer == form.answer.data:
            login_user(user)
            return redirect(url_for('change_pw'))
        else:
            flash("Das hat nicht geklappt. Hast du dich vielleicht vertippt?")



    return render_template('reset_pw.html', form = form)


# change password

@app.route('/change_pw', methods=['GET', 'POST'])
@login_required
def change_pw():
    pass_form = PasswordForm()

    if pass_form.validate_on_submit():
        current_user.set_password(pass_form.pw1.data)
        db.session.commit()
        flash("Dein Passwort wurde erfolgreich geändert.")
        return redirect(url_for('home'))

    return render_template('change_pw.html', pass_form=pass_form)


# chat view
# display chat between current user and a match

@app.route('/chat/<matchid>', methods=['GET', 'POST'])
@login_required
def chat(matchid):

    msg_form = MsgForm()

    if msg_form.validate_on_submit():
        # if form is submited match id becomes chat id
        try:
            # get chat and add new mesage
            chat = Chat.query.get(matchid)
            msg = Msg(chat=chat.id, user=current_user.id, msg_data=msg_form.msg.data)
            db.session.add(msg)
            db.session.commit()

            msg = Msg.query.filter_by(chat=chat.id).all()
            user = chat.users
            user.remove(current_user)
            user = user.first()

            return render_template('chat.html', msgs=msg, user=user, msg_form = msg_form, chatid = chat.id)
        except:
            return redirect(url_for('matches'))

    # get match or 404 match is chat partner
    match = User.query.filter_by(id=matchid).first_or_404()
    chats = current_user.chats

    # get the chat between current user and match out of db
    for chat in chats:
        if match in chat.users:
            # get all msgs of chat
            msg = Msg.query.filter_by(chat=chat.id).all()
            user = chat.users
            user.remove(current_user)
            user = user.first()
            # also set chat id. It is used if new mesages are added
            return render_template('chat.html', msgs=msg, user=user, msg_form = msg_form, chatid = chat.id)

    return redirect(url_for('matches'))


# about view
# display info about schinder company and team

@app.route('/about')
def about():
    return render_template('about.html')


# admin section

@app.route('/admin', methods=['get', 'post'])
@login_required
def admin():
    try:
        user_id = session['_user_id']
        this_user = User.query.get(int(user_id))
        if ( not this_user.roll.upper() == 'A'):
            return render_template('noadmin.html')
    except Exception as e:
        return render_template('noadmin.html')

    search = SearchForm()

    if search.validate_on_submit():
        # get all msgs od user
        myUser = User.query.filter_by(username=search.search.data).first()
        msgs = Msg.query.filter_by(user=myUser.id).all()
        msg_recipients = []

        # get msg recipient
        for msg in msgs:
            chat_id = msg.chat
            chat = Chat.query.filter_by(id = chat_id).first()
            for user in chat.users:
                if user != myUser:
                    msg_recipients.append(user.username)


        return render_template('admin.html', form=search, msgs=msgs, msg_recipients= msg_recipients, user=myUser)
    else:
        if search.errors:
            flash("Diese User gibt es nicht. Schreib man ihn anders?")
        return render_template('admin.html', form=search)


# JIM! do we still need this? Is your cat laying on your keyboard again or why is this stil here?
# TODO: remove this from production
# show all reg users
@app.route('/admin_show_all_users_in_system', methods=['get', 'post'])
@login_required
def admin_all_users():

    all_users = User.query.all()
    return render_template('all_user.html', all_users = all_users)

# get usermail by mail

@app.route('/usermail', methods=['get', 'post'])
@login_required
def usermail():
    # check if admin
    if current_user.roll != 'a':
        return render_template('noadmin.html')

    form = SQLForm()
    text = ""
    if form.validate_on_submit():

        # must be abslolut path on server
        # engine = create_engine('sqlite:////home/Schinder/mysite/sse_schinder/app.db')
        
        engine = create_engine('sqlite:///app.db')

        with engine.connect() as con:
            userInput = str(form.input.data)
            injection = 'SELECT email FROM user WHERE username=' + "\'" + userInput + "\';"

            if injection is not None:
                rs = con.execute(injection)
                print(type(rs))
                print(rs)
                for row in rs:
                    text = text +  str(row)
    print(text)
    return render_template('usermail.html', form=form, texts=text)
