"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'ItsAWonderfulLife'
app.config['DEBUG_TB_INTERCEPT-REDIRECTS'] = False
# app.run(debug=True)
debug = DebugToolbarExtension(app)

app.app_context().push()

connect_db(app)
db.create_all()

@app.route('/')
def show_home_page():
    '''temp redirect to user list'''
    return redirect('/users')

@app.route('/users')
def show_user_list():
    '''Query database for all users, then render html with user list'''
    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/users/<user_id>')
def show_user_details(user_id):
    '''Query database for user with matching user_id'''
    user = User.query.get(user_id)
    return render_template('user_detail.html', user=user)

@app.route('/users/<user_id>/edit')
def show_edit_user_form(user_id):
    '''Render the edit user page for the user with matching id'''
    user = User.query.get(user_id)
    return render_template('edit_user.html', user=user)

@app.route('/users/<user_id>/edit', methods=['POST'])
def edit_user_data(user_id):
    '''Query database for user with matching id, the take the values
    from the post request form and update the existing user in the database
    with those values'''
    user = User.query.get_or_404(user_id)

    user.first_name = request.form['first-name']
    user.last_name = request.form['last-name']
    user.image_url = request.form['image-url']

    db.session.add(user)
    db.session.commit()

    return redirect(f'/users/{user_id}')

@app.route('/users/new')
def show_new_user_form():
    '''render new user form page'''
    return render_template('add_user.html')

@app.route('/users/new', methods=['POST'])
def add_new_user():
    '''Add new user to the database by taking the values
    submitted in the HTTP request form and creating a new
    instance of the User class with those values'''
    new_user = User(first_name=request.form['first-name'], last_name=request.form['last-name'], image_url=request.form['image-url'])

    db.session.add(new_user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<user_id>/delete', methods=['POST'])
def delete_user(user_id):
    '''Delete a user from the database based off of the 
    matching user id.'''
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')