from models import User, db
from app import app

db.drop_all()
db.create_all()

# User.query.delete()

matt_c = User(first_name='Matt', last_name='Campbell', image_url='https://avatars.githubusercontent.com/u/114436937?v=4')
caroline_r = User(first_name='Caroline', last_name="Redmond")

db.session.add(matt_c)
db.session.add(caroline_r)

db.session.commit()