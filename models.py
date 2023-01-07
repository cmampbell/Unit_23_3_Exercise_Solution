"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

default_image= 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR82DN9JU-hbIhhkPR-AX8KiYzA4fBMVwjLAG82fz7GLg&s'

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    '''User model'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    first_name = db.Column(db.String, nullable=False)

    last_name = db.Column(db.String, nullable=False)

    image_url = db.Column(db.String, default=default_image)

    def __repr__(self):
        '''Update representation of user class'''
        u=self
        return f"<User id = {u.id}, User first_name= {u.first_name}, last name= {u.last_name}, image_url={u.image_url}>"

    



