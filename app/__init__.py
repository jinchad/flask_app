from flask import Flask
from config import Config
# package for managing the database interactions with ORM
from flask_sqlalchemy import SQLAlchemy

# package for handling database migrations
from flask_migrate import Migrate

# manages uers authentication and sessions
from flask_login import LoginManager

# Initializing the app as a Flask object
appy = Flask(__name__)
appy.config.from_object(Config)

# Initializing the database
db = SQLAlchemy(appy)
migrate = Migrate(appy, db)

# Creating a login manager object
login = LoginManager(appy)

# setting the view for the login object
login.login_view = 'login'

# import statement to prevent circular imports
from app import routes, models