# import packages
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy # package for managing the database interactions with ORM
from flask_migrate import Migrate # package for handling database migrations
from flask_login import LoginManager # package that manages uers authentication and sessions

appy = Flask(__name__) # Initializing the app as a Flask object
appy.config.from_object(Config)

db = SQLAlchemy(appy) # Initializing the database
migrate = Migrate(appy, db)

login = LoginManager(appy) # Creating a login manager object
login.login_view = 'login' # setting the view for the login object

from app import routes, models # import statement to prevent circular imports