"""Blogly application."""

from flask import Flask, request, render_template, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

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

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    '''Query database for user with matching user_id, show details page'''
    user = User.query.get(user_id)
    
    return render_template('user_detail.html', user=user, posts=user.posts)

@app.route('/users/<int:user_id>/edit')
def show_edit_user_form(user_id):
    '''Render the edit user page for the user with matching id'''
    user = User.query.get(user_id)
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
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

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    '''Delete a user from the database based off of the 
    matching user id.'''
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new')
def show_new_post_form(user_id):
    '''Show new post form for the user selected'''
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('new_post.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_new_post(user_id):
    '''Add new posts into the post table'''
    user = User.query.get_or_404(user_id)

    new_post = Post(title=request.form['title'], content=request.form['content'], user_id=user.id, created_at=db.sql.func.now())

    for tag_name in request.form.getlist('tags'):
        tag = Tag.query.filter(Tag.name == tag_name).one()
        new_post.tags.append(tag)
    
    db.session.add(new_post)
    db.session.commit()
    
    return redirect(f'/users/{user.id}')

@app.route('/posts/<int:post_id>')
def show_post_details(post_id):
    '''Show details for a specific post'''
    post = Post.query.get_or_404(post_id)
    tags = post.tags

    return render_template('post_detail.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit')
def show_edit_post_page(post_id):
    '''Show the edit post page for specific post'''
    post = Post.query.get_or_404(post_id)

    current_tags = post.tags
    all_tags = Tag.query.all()

    return render_template('edit_post.html', post=post, current_tags=current_tags, all_tags=all_tags)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def update_edited_post(post_id):
    '''Update a post in db based on post id and input form'''
    post = Post.query.get_or_404(post_id)

    post.title = request.form['title']
    post.content = request.form['content']

    #Check if an existing tag has been removed from the post
    for tag in post.tags:
        if tag.name not in request.form.getlist('tags'):
            post_tag = PostTag.query.filter(tag.id == PostTag.tag_id, post.id == PostTag.post_id).one()
            db.session.delete(post_tag)
        
    #Check tags in list and append new tags to post.tags array
    for tag_name in request.form.getlist('tags'):
        tag = Tag.query.filter(Tag.name == tag_name).one()
        if tag not in post.tags:
            post.tags.append(tag)

    db.session.add(post)
    db.session.commit()

    return redirect(f'/posts/{post.id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    '''Delete a post from the database based off of the 
    matching user id.'''
    post = Post.query.get(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{post.user_id}')

@app.route('/tags')
def show_all_tags():
    '''Show all tags to the user'''
    tags = Tag.query.all()
    return render_template('tag_list.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def show_tag_details(tag_id):
    '''Show all posts for a tag'''
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag_details.html', tag=tag, posts=tag.posts)

@app.route('/tags/new')
def show_new_tag_form():
    '''Show new tag form to user'''
    return render_template('add_tag.html')

@app.route('/tags/new', methods=['POST'])
def add_new_tag():
    '''Adds new tag to database based on user input'''
    tag = Tag(name=request.form['name'])

    db.session.add(tag)
    db.session.commit()

    return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit')
def show_tag_edit_form(tag_id):
    '''Render edit page for a specific tag'''
    tag = Tag.query.get_or_404(tag_id)

    return render_template('edit_tag.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def update_edited_tag(tag_id):
    '''Update the tag based on user input in edit tag form'''
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']

    db.session.add(tag)
    db.session.commit()

    return redirect(f'/tag/{tag.id}')

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    '''Delete specific tag'''
    tag = Tag.query.get(tag_id)

    db.session.delete(tag)
    db.session.commit()

    return redirect('/tags')
