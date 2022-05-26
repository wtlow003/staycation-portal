from typing import Callable

from app import db
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from flask_mongoengine import BaseQuerySet
from werkzeug.local import LocalProxy

# record all operations to execute when Staycation related operations are performed
staycation = Blueprint("staycation", __name__)


class Staycation(db.Document):
    """Staycation data model.

    The `Staycation` data model handles all staycation packages available for booking.
    All staycation documents created are stored in the database, under the collection `staycation`.

    The schema for the `Staycation` data model is declared
    based on `static/data/staycation.csv` (or `assets/data/staycation.csv`).

    In the raw data, the there are five (5) corresponding column names:
        1. `hotel_name`, the name of the hotel.
        2. `duration`, the duration of the staycation package.
        3. `unit_cost`, the daily unit cost of the staycation package.
        4. `image_url`, url for the staycation package display image.
        5. `description`, the description of the staycation package.

    The required fields of the `Staycation` document are:
        1. `hotel_name`: The name of the hotel, corresponding to `hotel_name` in raw data.
        2. `duration`: The duration of the staycation package, corresponding to `duration` in raw data.
        3. `unit_cost`: The daily unit cost of the staycation package, corresponding to `unit_cost` in raw data.
        4. `image_url`: The image url for the staycation display image, corresponding to `image_url` in raw data.
        5. `description`: The description of the staycation package, corresponding to `description` in raw data.
    """

    # all `Staycation` objects are stored as documents in collection `staycation`
    meta = {"collection": "staycation"}
    # `hotel_name` field is a String field, which is a Python string object, with max length of 30 characters
    hotel_name = db.StringField(max_length=30)
    # `duration` is a Integer field, which is a Python integer object
    duration = db.IntField()
    # `unit_cost` is a Float field, which is a Python float object
    unit_cost = db.FloatField()
    # `image_url` is a String field, which is a Python string object, with max length of 30 characters
    image_url = db.StringField(max_length=30)
    # `description` is a String field, which is a Python string object, with max length of 500 characters
    description = db.StringField(max_length=500)


@staycation.route("/products")
@login_required
def render_product() -> Callable[[str, BaseQuerySet, LocalProxy, str], str]:
    """Packages (products) route endpoint.

    Args:
        GET: /products

    Returns:
        Callable[[str, BaseQuerySet, LocalProxy, str], str]: Renders the Packages page using `products.hmtl` template.
    """
    # retrieve all products from db
    products = Staycation.objects()
    # return products html page by default
    return render_template(
        "packages.html", products=products, user=current_user, panel="Products"
    )
