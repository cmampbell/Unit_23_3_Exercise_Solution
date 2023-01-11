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

    posts = db.relationship('Post', backref='user')

    def __repr__(self):
        '''Update representation of user class'''
        u=self
        return f"<User id = {u.id}, User first_name= {u.first_name}, last name= {u.last_name}, image_url={u.image_url}>"

class Post(db.Model):
    '''Post model'''

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    post_tag = db.relationship('PostTag', backref='post', passive_deletes=True)
    tags = db.relationship('Tag', secondary='post_tags', backref='posts')

    def __repr__(self):
        '''Update representation of Post class'''
        p=self
        return f'<post_id= {p.id}, title={p.title}, content={p.content}, created_at={p.created_at}, user_id={p.user_id}'

class Tag(db.Model):
    '''Tag model'''

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)

    post_tag = db.relationship('PostTag', backref='tag', passive_deletes=True)

    def __repr__(self):
        '''Update representation of Tags class'''
        t = self
        return f'<tag_id={t.id}, tag_name={t.name}>'

class PostTag(db.Model):
    '''Post Tag many to many table Model'''

    __tablename__ = 'post_tags'

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id',  ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
