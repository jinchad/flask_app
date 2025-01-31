# import packages
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy # package for managing the database interactions with ORM
from flask_migrate import Migrate # package for handling database migrations
from flask_login import LoginManager # package that manages uers authentication and sessions
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

appy = Flask(__name__) # Initializing the app as a Flask object
appy.config.from_object(Config)

db = SQLAlchemy(appy) # Initializing the database
migrate = Migrate(appy, db)

login = LoginManager(appy) # Creating a login manager object
login.login_view = 'login' # setting the view for the login object

# if statement to check if the app is running without debug mode, only running code below if so
if not appy.debug:
    if appy.config['MAIL_SERVER']: # if statement checkinf if email server exists in configuration
        auth = None
        if appy.config['MAIL_USERNAME'] or appy.config['MAIL_PASSWORD']:
            auth = (appy.config['MAIL_USERNAME'], appy.config['MAIL_PASSWORD'])
        secure = None
        if appy.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(appy.config['MAIL_SERVER'], appy.config['MAIL_PORT']),
            fromaddr='no-reply@' + appy.config['MAIL_SERVER'],
            toaddrs=appy.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        appy.logger.addHandler(mail_handler)
        
    # if statement checking if logs directory exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', 
                                       maxBytes=10240, #max log size is 10kb
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    appy.logger.addHandler(file_handler)

    appy.logger.setLevel(logging.INFO)
    appy.logger.info('Microblog startup')

from app import routes, models, errors # import statement to prevent circular imports