from typing import Optional
import sqlalchemy as sa # package for general purpose database functions and classes such as types and query building helpers
import sqlalchemy.orm as so # package that provides support for model
from app import db, login
from hashlib import md5
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

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)


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
    username: so.Mapped[str] = so.mapped_column(sa.String(64), 
                                                index=True,
                                                unique=True # ensures that only a single instance of this username is allowed in the column
                                                )
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))

    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, # configures the association table used for the relationship
        primaryjoin=(followers.c.follower_id == id), # indicates condition linking entity to the association table
        secondaryjoin=(followers.c.followed_id == id), # indicates condition linking association table to the user on the other side of the relationship
        back_populates='followers')
    
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, 
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
    
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
    
    # generating the avatar using Gravatar service
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author)) # joining user_id under post db to author
            .join(Author.followers.of_type(Follower), isouter=True) # joining user_id of author to user_id of follower
            .where(sa.or_(
                Follower.id == self.id, # filter out all posts that are not posted by users followed by this target user
                Author.id == self.id, # filter out all posts not posted by the user
            )) 
            .group_by(Post) # prevents duplicated posts by the same user
            .order_by(Post.timestamp.desc())
        )


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
