from unittest import TestCase

from app import app
from models import db, User, Post

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.app_context().push()

db.drop_all()
db.create_all()

class UsersViewsTestCase(TestCase):
    '''Tests for view functions concering users'''

    def setUp(self):
        '''Delete users in database, set up new fake user in db before every test'''
        Post.query.delete()
        User.query.delete()

        user = User(first_name='Test', last_name='User', image_url='https://st.depositphotos.com/1005858/1815/i/950/depositphotos_18158715-stock-photo-regular-guy-full-body-shot.jpg')

        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user_fname = user.first_name
        self.user_lname = user.last_name

    def tearDown(self):
        '''Clear out session transactions'''

        db.session.rollback()

    def test_show_users(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test User', html)
    
    def test_show_user_details(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<img src=', html)
            self.assertIn(f'<form action="/users/{self.user_id}/edit">', html)
            self.assertIn(f'{self.user_fname} {self.user_lname}', html)

    def test_show_edit_user_form(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.user_fname, html)
            self.assertIn(self.user_lname, html)
            self.assertIn('<button type="submit">Cancel</button>', html)
            self.assertIn(f'formaction="/users/{self.user_id}/edit"', html)

    def test_edit_user_data(self):
        with app.test_client() as client:
            d = {'first-name': 'Honey', 'last-name': 'Milk', 'image-url':'https://thumbs.dreamstime.com/b/regular-guy-7657297.jpg'}
            resp = client.post(f'/users/{self.user_id}/edit', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Honey Milk', html)

    def test_show_new_user_form(self):
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form action="/users/new" method="POST">', html)

    def test_add_new_user(self):
        with app.test_client() as client:
            d = {'first-name': 'Honey', 'last-name': 'Milk', 'image-url':'https://thumbs.dreamstime.com/b/regular-guy-7657297.jpg'}
            resp = client.post('/users/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Honey Milk', html)
            self.assertIn('Test User', html)
            self.assertIn('<form action="/users/new">', html)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post(f'/users/{self.user_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<ul>', html)
            self.assertEqual(len(User.query.all()), 0)

class PostsViewsTestCase(TestCase):
    '''Tests for view functions concerning posts'''
    def setUp(self):
        '''Delete posts and users in database, set up test users 
        and posts in db before every test'''

        Post.query.delete()
        User.query.delete()

        user = User(first_name='Test', last_name='User', image_url='https://st.depositphotos.com/1005858/1815/i/950/depositphotos_18158715-stock-photo-regular-guy-full-body-shot.jpg')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Yeehaw', content='Ride that horse cowboy', user_id=user.id, created_at=db.sql.func.now())
        db.session.add(post)
        db.session.commit()

        self.user_id = user.id
        self.user_fname = user.first_name
        self.user_lname = user.last_name
        self.user_posts = user.posts

        self.post_id = post.id
        self.post_title = post.title
        self.post_content = post.content
        self.post_user_id = post.user_id

    def tearDown(self):
        '''Clear out session transactions'''

        db.session.rollback()

    def test_show_new_post_form(self):
        '''Tests app to see if it renders post on appropriate user'''
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/posts/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>Add post for {self.user_fname} {self.user_lname}</h1>', html)

    def test_add_new_post(self):
        '''Tests app to see if it adds post to posts table'''
        with app.test_client() as client:
            d = {'title': 'Woohoo', 'content': 'testing is a party', 'created_at': db.sql.func.now(), 'user_id':self.user_id}
            resp = client.post(f'/users/{self.user_id}/posts/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Woohoo', html)
            self.assertIn('<li>', html)

    def test_show_post_details(self):
         with app.test_client() as client:
            resp = client.get(f'/posts/{self.post_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h2>{self.post_title}</h2>', html)
            self.assertIn(f'<button type="submit" formaction="/posts/{self.post_id}/delete"', html)
            self.assertIn(f'<button type="submit" formaction="/users/{self.post_user_id}">', html)

    def test_show_edit_post_page(self):
        with app.test_client() as client:
            resp = client.get(f'/posts/{self.post_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Yeehaw', html)
            self.assertIn('<input type="Submit" value="Save">', html)

    def test_update_edited_post(self):
        with app.test_client() as client:
            d = {'title': 'Woohoo', 'content': 'testing is a party', 'created_at': db.sql.func.now(), 'user_id':self.user_id}
            resp = client.post(f'/posts/{self.post_id}/edit', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Woohoo', html)
            self.assertIn('<button type="submit">Edit</button>', html)

    def test_delete_post(self):
        with app.test_client() as client:
            resp = client.post(f'/posts/{self.post_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(Post.query.all()), 0)