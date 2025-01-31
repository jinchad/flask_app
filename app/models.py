from typing import Optional
import sqlalchemy as sa # package for general purpose database functions and classes such as types and query building helpers
import sqlalchemy.orm as so # package that provides support for model
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader # decorator that tells Flask-Login how to load user from the database based on the user id
def load_user(id):
    """
    function is used to load the user from the database based on the given id

    Flask-Login cannot connect directly with the db, hence the extension expects that the application will configure a user loader function, that can be called to load a user given the ID.

    Args:
        id (str): a string denoting the target user id 

    Returns:
        User: user retrieved from database
    """
    return db.session.get(entity= User, ident = int(id))

class User(db.Model, UserMixin):
    """
    This class is used to store the parameters and methods associated with a User object.
    
    This class is a child of the following:
        - db.Model: This packages makes the User class a database model in SQLAlchemy, where the parameters in this class becomes columns stored in the database
        - UserMixin: This is a Flask-login mixin that implements user authentication methods 

    Attributes:
        - id (int): user id of the account
        - username (str): account's username
        - email (str): account's email
        - posts (Post): Posts made under the account
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True) 
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    def __repr__(self):
        """
        string representation of the User class.

        Returns:
            username (str): username of the user.
        """
        username = '<User {}>'.format(self.username)
        return username
    
    def set_password(self, password):
        """
        used to set password of the user with a hash
        """
        # generating a hash for the password and setting it as an attribute for the class
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        checks if the input password is identical to that of the user's hashed password 

        Args:
            - password (str): password to be checked
        
        Returns:
            - boolean value indicating if the password given is identical to that of the user
        """
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')
    # so.relationship() to map Post User ID to author ID

    def __repr__(self):
        return '<Post {}>'.format(self.body)
