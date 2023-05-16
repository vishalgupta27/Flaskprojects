from flask_sqlalchemy import SQLAlchemy

from Flask2023 import db, app
from flask_migrate import Migrate

# db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    number = db.Column(db.Integer)

    def __init__(self, username, email, password, number):
        self.username = username
        self.email = email
        self.password = password
        self.number = number


# with app.app_context():
#     db.create_all()


# with app.app_context():
#     # Create a new user and add it to the database
#     new_user = User(username='arvind', email='arvind@co.in',password=None)
#     db.session.add(new_user)
#     db.session.commit()

with app.app_context():
    # Retrieve the user from the database
    user = User.query.get(1)  # Replace 1 with the actual user ID

    # Update the username and email
    user.username = 'new_username'
    user.email = 'new_email@example.com'

    # Commit the changes to the database
    db.session.commit()
#
# def delete_user():
#     with app.app_context():
#         # Drop the User table
#         xyz.__table__.drop(db.engine)


class Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=False, nullable=False)
    last_name = db.Column(db.String(20), unique=False, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # repr method represents how one object of this datatable
    # will look like
    def __repr__(self):
        return f"Name : {self.first_name}, Age: {self.age}"
