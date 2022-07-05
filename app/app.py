from csv import DictReader
from io import StringIO
from typing import Callable

from flask import render_template, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app import app, login_manager
from auth import auth
from book import booking, Booking
from dashboard import dashboard
from staycation import staycation, Staycation
from users import User

# register authentication-related operations
app.register_blueprint(auth)
# register booking-related operations
app.register_blueprint(booking)
# register staycation-related operations
app.register_blueprint(staycation)
# register dashboard-related operations
app.register_blueprint(dashboard)


# load current user if (any)
@login_manager.user_loader
def load_user(user_id) -> User:
    """Retrieve current user credentials.

    Args:
        user_id (str): _id of User object in `User` document.

    Returns:
        User: User object.
    """
    return User.objects(pk=user_id).first()


@app.route("/")
def show_base() -> Callable[[str], str]:
    """Base route endpoint.

    Returns:
        Callable[[str], str]: Renders the base page using `base.hmtl` template.
    """
    return render_template("base.html")


def _upload_db_processing_logic(reader: DictReader, file_type: str) -> None:
    """Perform file processing logic to generate appropriate data model objects in either,
    ["Staycation", "Booking", "User"].items

    For each data model, objects are to processed seperately based on different fields required.

    Args:
        reader (DictReader): Reader for CSV file uploaded, with fields as keys in dictionary.
        file_type (str): Type of file uploaded, either "Staycations", "Bookings" or "Users".
    """
    for item in list(reader):
        if file_type == "staycation":
            # create staycation document
            staycation = Staycation(**item)
            # save to db
            staycation.save()
        elif file_type == "booking":
            # preprocessing to retrieve user and staycation references
            user_ref = User.objects(email=item["customer"]).first()
            staycation_ref = Staycation.objects(hotel_name=item["hotel_name"]).first()
            # update the data dict required
            updated_item = {
                "check_in_date": item["check_in_date"],
                "customer": user_ref,
                "package": staycation_ref,
            }
            # create booking document
            booking = Booking(**updated_item)
            # compute total cost of booking and update
            booking.calculate_total_cost()
            # save to db
            booking.save()
        else:
            # retrieve number of users with same email
            # that is about to be created and stored in DB
            existing_user = User.objects(email=item["email"]).count()
            # if no existing user available, create new user
            if not existing_user:
                hashpass = generate_password_hash(item["password"], method="sha256")
                credentials = User(
                    email=item["email"], password=hashpass, name=item["name"]
                )
                # save to db
                credentials.save()


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload() -> Callable[[str, str, str], str]:
    """Upload route endpoint.

    Handles logic to pre-process CSV file and upload to MongoDB, for various file types
    in ["Staycation", "Booking", "User"].

    Args:
        GET: /upload
        POST: /upload

    Returns:
        Callable[[str, str, str], str]: Renders the upload page using `upload.hmtl` template.
    """
    if request.method == "POST":
        # retrieve file uploaded and read data into DictReader
        file = request.files.get("file")
        # `file_type` determines which data model to use for processing
        # and saving to document collection
        file_type = request.form.get("datatype")
        data = file.read().decode("utf-8")
        reader = DictReader(StringIO(data), delimiter=",", quotechar='"')
        # conduct processing logic for file uploaded based on specified file type
        _upload_db_processing_logic(reader, file_type)
    # return upload html page by default if GET request
    return render_template("upload.html", panel="Upload")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
