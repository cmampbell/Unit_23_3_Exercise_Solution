from unittest import TestCase

from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.app_context().push()

db.drop_all()
db.create_all()

class UsersViewsTestCase(TestCase):
    '''Tests for Users Model'''

    def setUp(self):
        '''Delete users in database, set up new fake user in db before every test'''

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


    
    
        