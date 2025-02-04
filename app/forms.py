# importing necessary packages
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    """
    LoginForm class that stores the necessary fields for the login page. 
    
    The LoginForm class inherits from the FlaskForm class and stores fields used to create the login page in login.html

    Attributes:
        username (StringField): used in creation of the username field that only accepts a string input
        password (PasswordField): creates the password field
        remember_me (BooleanField): creates a tick that allows users to choose to remain logged in
        submit (SubmitField): creates a sign in button
    """

    username = StringField(label = 'Username', 
                           validators=[DataRequired()] # DataRequired() ensures that the password field cannot be left empty
                           )
    """
    StringField for the username field in the user login page
    
    - label (str): label for the email field, set to "Username"
    - validators (list): a list containing the validators for this particular field, which includes:
        - DataRequired(): ensures that this field must be filled in

    Type:
        StringField
    """

    # Password field for password
    password = PasswordField(label ='Password', 
                             validators=[DataRequired()] # DataRequired() ensures that the password field cannot be left empty
                             )
    """
    PasswordField for the password field in the user login page
    
    - label (str): label for the email field, set to "Password"
    - validators (list): a list containing the validators for this particular field, which includes:
        - DataRequired(): ensures that this field must be filled in

    Type:
        PasswordField
    """

    remember_me = BooleanField(label = 'Remember Me') # boolean field that allows user the option to remain logged in

    submit = SubmitField(label = 'Sign In') # creates the sign in button


class RegistrationForm(FlaskForm):
    """
    RegistrationForm class stores all fields used in creation of the registration page

    The RegistrationForm class is a child of the FlaskForm class and stores fields used to create the registration page in register.html

    Attributes:
        username (StringField): creates a username field that only accepts String inputs
        email (StringField): creates the email field
        password (PasswordField): creates the password setting field
        password2 (PasswordField): creates the confirm password field
        submit (SubmitField): creates the submit button
    """

    username = StringField(label = 'Username', 
                           validators=[DataRequired()]
                            )
    """
    StringField for the username field in the user registration page
    
    - label (str): label for the email field, set to "Username"
    - validators (list): a list containing the validators for this particular field, which includes:
        - DataRequired(): ensures that this field must be filled in

    Type:
        StringField
    """

    email = StringField(label = 'Email', 
                        validators=[DataRequired(), 
                                    Email()]
                                    )
    """
    StringField for the email field in the user registration page
    
    - label (str): label for the email field, set to "Email"
    - validators (list): a list containing the validators for this particular field, which includes:
        - DataRequired(): ensures that this field must be filled in
        - Email(): ensures that input for this field must be a valid email address

    Type:
        StringField
    """

    password = PasswordField(label = 'Password', 
                             validators=[DataRequired()]
                             )
    """
    PasswordField for the password field in the user registration page
    
    - label (str): label for the password field, set to "Password"
    - validators (list): a list containing the validators for this particular field, which includes DataRequired() which ensures that this field must be filled in

    Type:
        PasswordField
    """
    
    password2 = PasswordField(
        label = 'Repeat Password', 
        validators=[DataRequired(), 
                    EqualTo('password')
                    ]
                )
    """
    PasswordField confirmation field for the reconfirm password field in the user registration page
    
    - label (str): label for the password field, set to "Repeat Password"
    - validators (list): a list containing the validators for this particular field, which includes:
        - DataRequired(): ensures that this field must be filled in
        - EqualTo('password'): ensures that input for this field must be identical to that of 'password'

    Type:
        PasswordField
    """
    
    submit = SubmitField('Register') # creates a register button

    def validate_username(self, username):
        """
        This method checks if the username is already use in the database

        Attributes:
            username: username to be validated
        """
        # retrieving any existing users in the database based on the username
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        
        # if statement checking if any users have been found and raising a ValidationError if so
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """
        This method checks if the email is already registered with an existing user in the database

        Attributes:
            email: email to be validated
        """
        # retrieving any existing users based on the email
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        
        # if statement checking if any users have been found and raising a ValidationError if so
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')
            
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
