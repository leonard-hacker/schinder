from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import InputRequired, ValidationError, Email, EqualTo, Regexp    
from .models import User, Topic, Safety_question

import re

try:
    all_questions = Safety_question.query.all()
except:
    all_questions = []

all_questions_name = []

for question in all_questions:
    all_questions_name.append(question.question)


class LoginForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired()])
    password = PasswordField('Password', validators = [InputRequired()])
    remember_me = BooleanField('Daten speichern')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    roll = StringField('Roll', default='U')
    username = StringField('Nickname', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Regexp('\d+@stud\.hs-mannheim\.de', message="Du brauchst eine Mail der HS-Mannheim. Z.b. '1234567@stud.hs-mannheim.de.'")])
    password = PasswordField('Passwort', validators=[InputRequired()])
    password2 = PasswordField('Eingabe wiederholen', validators=[InputRequired(), EqualTo('password', message="Die beiden Passwörter müssen übereinstimmen.")]) 

    safety_question = SelectField(choices=all_questions_name, validators=[InputRequired()])
    answer = StringField('Antwort', validators=[InputRequired()])

    submit = SubmitField('registrieren')

    def validate_password(self, password):
        """
        Verify the strength of 'password'
        Returns a dict indicating the wrong criteria
        A password is considered strong if:
            8 characters length or more
            1 digit or more
            1 symbol or more
            1 uppercase letter or more
            1 lowercase letter or more
        """

        # checking the length
        if len(password.data) < 8:
            raise ValidationError('Dein Passwort muss mindestens 8 zeichen lang sein.')

        # checking for digits
        if re.search(r"\d", password.data) is None:
            raise ValidationError('Dein Passwort muss mindestens eine Ziffer enthalten.')

        # checking for uppercase
        if re.search(r"[A-Z]", password.data) is None:
            raise ValidationError('Dein Passwort muss mindestens einen Großbuchstaben enthalten.')

        # checking for lowercase
        if re.search(r"[a-z]", password.data) is None:
            raise ValidationError('Dein Passwort muss mindestens einen Kleinbuchstaben enthalten.')

        # checking for symbols
        if re.search(r"\W", password.data) is None:
            raise ValidationError('Dein Passwort muss mindestens eine Sonderzeichen enthalten.')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Dieser Name ist bereits vergeben. Bitte benutz einen anderen.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Mit dieser Mail gibt es bereits einen Account.')

# edit profile
class ProfilForm(FlaskForm):
    try:
        all_topic = Topic.query.all()
    except:
        all_topic = []
        
    all_topic_name = []

    for topic in all_topic:
        all_topic_name.append(topic.name)

    discription = TextAreaField('Kurzbeschreibung')
    topic_select = SelectField(u'Programming Language', choices = all_topic_name)

    save = SubmitField('speichern')
    add = SubmitField('+/-')

# Form to change password in profile view
class PasswordForm(FlaskForm):
    pw1 = PasswordField('Passwort', validators=[InputRequired()])
    pw2 = PasswordField('Eingabe wiederholen', validators=[InputRequired(), EqualTo('pw1', message="Die beiden Passwörter müssen übereinstimmen.")])

    change = SubmitField('ändern')

    def validate_pw1(self, pw1):
            """
            Verify the strength of 'password'
            Returns a dict indicating the wrong criteria
            A password is considered strong if:
                8 characters length or more
                1 digit or more
                1 symbol or more
                1 uppercase letter or more
                1 lowercase letter or more
            """
            password = pw1.data

            # checking the length
            if len(password) < 8:
                raise ValidationError('Dein Passwort muss mindestens 8 zeichen lang sein.')

            # checking for digits
            if re.search(r"\d", password) is None:
                raise ValidationError('Dein Passwort muss mindestens eine Ziffer enthalten.')

            # checking for uppercase
            if re.search(r"[A-Z]", password) is None:
                raise ValidationError('Dein Passwort muss mindestens einen Großbuchstaben enthalten.')

            # checking for lowercase
            if re.search(r"[a-z]", password) is None:
                raise ValidationError('Dein Passwort muss mindestens einen Kleinbuchstaben enthalten.')

            # checking for symbols
            if re.search(r"\W", password) is None:
                raise ValidationError('Dein Passwort muss mindestens eine Sonderzeichen enthalten.')
        

# jope or nope matches
class MatchForm(FlaskForm):
    yes = SubmitField(' ')
    no = SubmitField(' ')

# send msg
class MsgForm(FlaskForm):
    msg = TextAreaField('SCHREIB EINE NACHRICHT', validators=[InputRequired()])
    send = SubmitField('senden')
    
#secret admin interface has a search field 
class SearchForm(FlaskForm):
    search = StringField('Username', validators = [InputRequired()])
    submit = SubmitField('Suche nach Nutzerchats')
    
    def validate_search(self, search ):
        user = User.query.filter_by(username=search.data).first()
        if user is None:
            raise ValidationError('Diese User gibt es nicht. Schreib man ihn anders?')

class SQLForm(FlaskForm):
    input = StringField('injection', validators=[InputRequired()])
    submit = SubmitField('Drück mich!')

# reset pw
class ResetPw(FlaskForm):
    username = StringField('Nickname', validators=[InputRequired()])
    safety_question = SelectField(choices=all_questions_name, validators=[InputRequired()])
    answer = StringField('Antwort', validators=[InputRequired()])
    submit = SubmitField('zurücksetzen')

