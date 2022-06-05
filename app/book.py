from typing import Callable

from flask import Blueprint, render_template, request
from flask_login import current_user

from app import app, db
from forms import BookingForm
from users import User
from staycation import Staycation

# record all operations to execute when booking related operations are performed
booking = Blueprint("booking", __name__)


class Booking(db.Document):
    """Booking data model.

    The `Booking` data model handles all booking made by users for the relevant staycation package.
    All booking documents created are stored in the database, under the collection `booking`.

    The schema for the `Booking` data model is declared
    based on `static/data/booking.csv` (or `assets/data/booking.csv`).

    In the raw data, the there are three (3) corresponding column names:
        1. `check_in_date`, the date of the booking check-in.
        2. `customer`, the name of the customer.
        3. `hotel_name`, the name of the hotel.

    The required fields of the `Booking` document are:
        1. `check_in_date`: Check-in date for booking, corresponding to `check_in_date` in raw data.
        2. `customer`: The `User` object that made the booking, identifed by the `customer`, corresponding to `customer` in raw data.
        3. `package`: The `Staycation` object booked, identifed by the `hotel_name`, corresponding to `hotel_name` in raw data.
        4. `total_cost`: Computed given `package` field, with `package.unit_cost` and `package.duration`, using `calculate_total_cost()` method.
    """

    # all `Booking` objects are stored as documents in collection `booking`
    meta = {"collection": "booking"}
    # mandatory DateTime field for the `Booking` object, corresponding to `check_in_date` in raw data
    # `check_in_date` field is a DateTime object, which is a Python datetime object, formatted as (%Y-%m-%d %H:%M:%S)
    check_in_date = db.DateTimeField(required=True)
    # references for `User` document stored under collection `appUsers`, identified by `customer` in raw data
    customer = db.ReferenceField(User)
    # references for `Staycation` document stored under collection `staycation`, identified by `hotel_name` in raw data
    package = db.ReferenceField(Staycation)
    # computed using the `calculate_total_cost()` method, referencing to `package` field
    # `total_cost` field is a Float field, which is a Python float object
    total_cost = db.FloatField()

    def calculate_total_cost(self) -> float:
        """Compute total cost of the booking, given the hotel's daily unit cost and the minimum stay duration.

        To compute the overall cost for a staycation package incurrred during a booking:
            1. Get the daily unit cost of the hotel, `unit_cost` in Staycation object.
            2. Get the stay duration of the hotel, `duration` in Staycation object.

            Total cost of staycation package = unit_cost * duration

        Returns:
            float: Total cost of staycation package incurred for booking, given `unit_cost` and `duration` from `Staycation` object.
        """
        self.total_cost = self.package.duration * self.package.unit_cost


@booking.route("/view_hotel=<hotel_name>", methods=["GET", "POST"])
def book_hotel(hotel_name) -> Callable[[str, BookingForm, Staycation, str], str]:
    """Booking route endpoint.

    Args:
        GET: /view_hotel=<hotel_name>
        POST: /view_hotel=<hotel_name>
        hotel_name (str): Name of hotel to be booked.

    Returns:
        Callable[[str, BookingForm, Staycation, str], str]: HTML template for hotel booking.
    """
    # retrieve the hotel data given hotel name for the template
    data = Staycation.objects(hotel_name=hotel_name).first()
    form = BookingForm()
    if request.method == "POST" and form.validate():
        # validate the date via `booking.BookingForm` and save booking to db
        # preprocessing to get staycation and user references
        user_ref = User.objects(email=current_user.email).first()
        staycation_ref = Staycation.objects(hotel_name=hotel_name).first()
        # create new staycation booking for hotel
        booking = Booking(
            check_in_date=form.date.data,
            customer=user_ref,
            package=staycation_ref,
        )
        # computing total cost for booking
        booking.calculate_total_cost()
        booking.save()
        # logging to ensure booking is saved
        app.logger.info(
            f"Booking saved: {(booking.check_in_date, booking.customer, booking.package)}"
        )
    # return booking html page by default if GET request
    return render_template("booking.html", form=form, hotel=data, panel=hotel_name)
