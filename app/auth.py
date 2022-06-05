from typing import Callable, Union

from flask import Blueprint, Response, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import app
from forms import RegForm
from users import User

# record authentication-related operations
auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
@auth.route("/")
def login() -> Union[
    Callable[[Callable[[str], str]], Response], Callable[[str, RegForm, str], str]
]:
    """Login route endpoint.

    Handles the staycation portal login template and logic.

    Args:
        GET: /login
        POST: /products
    Returns:
        Union[Callable[[Callable[[str], str]], Response], Callable[[str, RegForm, str], str]: Package (product)
            page if logged in or HTML template for staycation portal login.
    """
    form = RegForm()
    # if POST request, validate form
    if request.method == "POST" and form.validate():
        # check if user alreadt exists
        check_user = User.objects(email=form.email.data).first()
        if check_user:
            # existing user found, check password
            if check_password_hash(check_user["password"], form.password.data):
                # if password matched, login user
                login_user(check_user)
                # redirect user to package page
                return redirect(url_for("staycation.render_product"))
            # user found but invalid password
            form.password.errors.append("User Password is Incorrect!")
        # if no existing user found
        form.email.errors.append("No Such User!")
    # return login page by default if GET request
    return render_template("login.html", form=form, panel="Login")


# QN1B, QN2A
@auth.route("/register", methods=["GET", "POST"])
def register() -> Union[
    Callable[[Callable[[str], str]], Response], Callable[[str, RegForm, str], str]
]:
    """Register route endpoint.

    Handles the staycation portal registration template and logic.

    Args:
        GET: /register
        POST: /products
    Returns:
        Union[Callable[[Callable[[str], str]], Response], Callable[[str, RegForm, str], str]]: Package (product)
            page if logged in or HTML template for staycation portal registration.
    """
    form = RegForm()
    # if POST request, validate form
    if request.method == "POST" and form.validate():
        # check if form details already belongs to existing user
        existing_user = User.objects(email=form.email.data).first()
        if not existing_user:
            # encrypt password
            hashpass = generate_password_hash(form.password.data, method="sha256")
            # generate new user details
            credentials = User(
                email=form.email.data, password=hashpass, name=form.name.data
            )
            # save to `Users` collection
            credentials.save()
            app.logger.info(f"New User Created: {credentials.email}")
            login_user(credentials)
            # redirect logged in user to package page
            return redirect(url_for("staycation.render_product"))
        # if existing credentials is already found (cannot register user twice)
        form.email.errors.append("User Already Exists!")
        # return register page with errors for rendering
        render_template("register.html", form=form, panel="Register")
    # return register page by default if GET request
    return render_template("register.html", form=form, panel="Register")


@auth.route("/logout", methods=["GET"])
@login_required
def logout() -> Callable[[Callable[[str], str]], Response]:
    """Logout route endpoint.

    Redirect users to login page after user logged out. This is only valid
    when user is already signed in.

    Args:
        GET: /login (redirect to login page)
    Returns:
        Callable[[Callable[[str], str]], Response]: Redirect to HTML template for login.
    """
    logout_user()
    return redirect(url_for("auth.login"))
