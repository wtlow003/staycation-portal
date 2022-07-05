from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager


def create_app():
    # create an instance of the Flask WSGI application
    app = Flask(__name__)
    # defining the database URI
    app.config["MONGODB_SETTINGS"] = {"db": "eca", "host": "mongodb"}
    # setting path for all static files in application
    app.static_folder = "assets"
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    # setting up mongodb after app is initialise
    db = MongoEngine(app)

    # define secret key to use session, encrpyt cookies to browser
    app.config["SECRET_KEY"] = "90LWxND4o83j4K4iuop0"
    # enabling user management with LoginManager
    # logging in, logging out and remembering session
    login_manager = LoginManager()
    # configure login manager to work with initialised flask app
    login_manager.init_app(app)
    # view where user is redirected to when user is not logged in
    login_manager.login_view = "login"

    return app, db, login_manager


# initialise flask app and return app, db and login_manager
app, db, login_manager = create_app()
