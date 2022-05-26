from app import db
from flask_login import UserMixin


class User(UserMixin, db.Document):
    """User data model.

    The `User` data model handles all users registered on the platform.
    All user documents created are stored in the database, under the collection `appUsers`.

    As user login requires several authenticaion properties, it inherits UserMixin
    which provides implementation of these properties.

    The schema for the `User` data model is declared
    based on `static/data/users.csv` (or `assets/data/users.csv`).

    In the raw data, the there are three (3) corresponding column names:
        1. `email`, the email of the user.
        2. `password`, the password of the user.
        3. `name`, the name of the user.

    The required fields of the `User` document are:
        1. `email`: The email of the user, corresponding to `email` in raw data.
        2. `password`: The password of the user, corresponding to `password` in raw data.
        3. `name`: The name of the user, corresponding to `name` in raw data.
    """

    # all `User` objects are store as documents in collection `appUsers`
    meta = {"collection": "appUsers"}
    # `email` is a String field, which is a Python string object, with max length of 30 characters
    email = db.StringField(max_length=30)
    # `password` is a String field, which is a Python string object
    password = db.StringField()
    # `name` is a String field, which is a Python string object
    name = db.StringField()
