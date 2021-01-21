from flask import Flask , Response
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
#this is a settup file, no easteregs here. keep trying
app = Flask(__name__,
            static_folder='./static')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
Bootstrap(app)

from app import routes, models
