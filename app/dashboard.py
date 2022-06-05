from typing import Callable, Dict, Union, Tuple, List

from flask import (
    Blueprint,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from app import db
from book import Booking
from staycation import Staycation
from users import User

# record all operations to execute when dashboard related operations are performed
dashboard = Blueprint("dashboard", __name__)


class Chart(db.Document):
    """Chart data model.

    The `Chart` data model handles all chart objects generated based on current bookings.
    All chart doucments created are stored in the database, under the collections `charts`.

    The schema for the `Chart` data model is declared
    based on storing key data required to generate a dashboard view
    using ChartJS.

    The required keys:
        1. `dates`: An array of unique dates which have staycation package booked.
        2. `start_date`: The earliest date where a staycation package is booked, as well as
            the left end for the x-axis label.
        3. `end_date`: The latest date where a staycation package is booked, as well as
            the right end for the x-axis label.
        4. `data`: Raw data of Hotel's booking income by date.
            E.g., {'Shangri-La Singapore': {'2022-01-27': 900.0,
                                            '2022-02-27': 1800.0,
                                            '2022-01-25': 900.0,
                                            '2022-02-25': 900.0,
                                            ...}
                    'Capella Singapore': {'2022-01-27': ...}
                    ...}
    """

    meta = {"collection": "charts"}
    dates = db.ListField()
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    data = db.DictField()

    def insert_data(self, data: Dict[str, Dict[str, float]]) -> None:
        """Insert the total booking income for each hotel by date.

        Update initial instantiated Chart object's fields from None to the values
        retrieved from the total booking income data.

        Args:
            data (Dict[str, Dict[str, float]]): Total booking income by hotels and dates.
        """
        # we need to retrieve the start and end date of the chart
        dates = set()
        # obtaining the x-axis labels
        # which is the unique dates in ascending order retrieve from all bookings
        for _, values in data.items():
            dates = dates.union(values.keys())
        # date should also be sorted with the earliest date as the first element
        dates = sorted(list(dates), reverse=False)
        start_date, end_date = dates[0], dates[-1]

        # we need to update the Chart object in DB
        self.update(
            __raw__={
                "$set": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "dates": dates,
                    "data": data,
                }
            },
        )

    def prepare_chart_dimension_and_label(
        self,
    ) -> Tuple[Dict[str, List[float]], List[str]]:
        """Prepare a dictionary of {Hotel1: [total_income1, total_income2, total_income3], Hotel2: [total_income1,...]...]}
        into the sub-chart for each hotel and x-axis labels in the form of an array of unique dates in ascending order
        for charting purposes.

        All hotel should have the same dimension of income array, where the length of the array is
        the total number of unique dates within the `Booking` document object, where each data point within array is a representation
        of the total booking income for each date, arranged in ascending order. If there is no booking income for a hotel for a date,
        we will insert a placeholder of "-1", which will be further process in javascript prior to charting.

        Returns:
            Tuple[Dict[str, List[float]], List[str]]: Tuple of chart dimensions and x-axis labels
                ({hotel: [total_income1, total_income2, total_income3]}, x-axis labels).
        """
        # given all the unique dates that occurred from the bookings
        # we will need to ensure that each hotel has the same dimension of x_axis_labels
        # this meant that for each date, each hotel should have a corresponding booking income data point
        # if a hotel does not have a booking income for a date, we will insert a placeholder of "-1"
        chart_dimension = {}
        for hotel in self.data:
            # each hotel should have an array of total booking income for each date
            # hence len(self.dates) is the dimension of the array
            # default value is "-1" so that we only update if we have booking income
            # on the specific day
            chart_dimension[hotel] = [-1] * len(self.dates)
            for date in self.dates:
                # for each unique date in ascending order in x_axis_labels
                # if the hotel has booking income on that date, we will insert the total income
                # by finding the index of the date in x_axis_labels and update the corresponding index
                # in the chart_dimension array for the hotel
                if date in self.data[hotel]:
                    chart_dimension[hotel][self.dates.index(date)] = self.data[hotel][
                        date
                    ]

        return chart_dimension, self.dates


class BarChart(db.Document):
    """Bar Chart data model.

    The `BarChart` data model handles all bar chart objects generated based on current bookings.
    All bar chartt documents created are stored in the database, under the collections `barCharts`.

    The schema for the `BarChart` data model is declared
    based on storing key data required to generate a dashboard view
    using ChartJS, for bar chart display due by user and hotel.
    """

    meta = {"collection": "barCharts"}
    data = db.DictField()
    target = db.StringField()

    def insert_data(self, data: Dict[str, Dict[str, float]], target: str) -> None:
        """Insert computed dictionary of {<`User`/`Hotel`>: <`No. of Bookings`>}.
        and the aggregation level of the data (user or hotel, with the specific user or hotel name).
        """
        self.update(
            __raw__={"$set": {"data": data, "target": target}},
        )

    def prepare_chart_dimension_and_label(
        self,
    ) -> Tuple[Dict[str, List[float]], List[str]]:
        """Generate the list of labels and values for plotting barchart in Chart.JS

        Returns:
            Tuple[Dict[str, List[float]], List[str]]: Tuple of chart dimensions and x-axis labels
        """
        return list(self.data.keys()), list(self.data.values())


def _compute_daily_booking_income(bookings: Booking) -> Dict[str, Dict[str, float]]:
    """Compute the total booking income for each hotel by date.

    Args:
        bookings (Booking): Bookings made and stored in `Booking` documents.
        staycations (Staycation): Staycation package available in `Staycation` documents.

    Returns:
        Dict[str, Dict[str, float]]: Total booking income by hotels and dates.
    """
    # keep track of daily booking income by hotels
    booking_income_by_hotels = {}

    # iterate through bookings
    # for each date, add up the total income, and add the hotel to the dict
    # e.g. {"hotel": {"date1" : "total_income1", "date2" : "total_income2"}}
    for booking in bookings:
        hotel = booking.package.hotel_name
        date = booking.check_in_date.strftime(
            "%Y-%m-%d"
        )  # storing dates as "YYYY-MM-DD"
        # total income for the hotel on the date = duration * unit_cost
        total_income = booking.total_cost
        # check if hotel is in the `daily_booking_by_hotels` dict
        if hotel not in booking_income_by_hotels:
            booking_income_by_hotels[hotel] = {date: total_income}
        # if hotel already exist, we just need to check if date already exists
        # if date exist, we add to the total income on the date so far
        # else, we create a new entry for the date, where value = total income
        elif date in booking_income_by_hotels[hotel]:
            booking_income_by_hotels[hotel][date] += total_income
        else:
            booking_income_by_hotels[hotel][date] = total_income

    return booking_income_by_hotels


def _compute_booking_due_by(due_by: str, target: str) -> Dict[str, int]:
    """Compute dictionary of {<`User`/`Hotel`>: <`No. of Bookings`>}.

    Args:
        due_by (str): Due by `User` or `Hotel`, where if `User`, we will count the
            number of bookings for different hotels. Else if `Hotel`, we will count the
            number of bookings for different users.
        target (str): Target `User` or `Hotel`, where we will by aggregate bookings by.

    Returns:
        Dict[str, int]: Total number of booking by either `User` or `Hotel`.
    """
    # declare dict to hold the booking due by `User` or `Hotel`
    bookings_due_by = {}
    for booking in Booking.objects.all():
        # different logic for dict computations by either `User` or `Hotel``
        if due_by == "user":
            if booking.customer.name == target:
                # if the user's booking for a hotel has already been tracked
                # we increase the count if we observe another booking
                if booking.package.hotel_name in bookings_due_by:
                    bookings_due_by[booking.package.hotel_name] += 1
                else:
                    # else we will track the booking for the hotel by user
                    bookings_due_by[booking.package.hotel_name] = 1
        # if we are not looking at `User` level we are looking by `Hotel``
        elif booking.package.hotel_name == target:
            if booking.customer.name in bookings_due_by:
                bookings_due_by[booking.customer.name] += 1
            else:
                # else we will track the user booking for the hotel
                bookings_due_by[booking.customer.name] = 1

    return bookings_due_by


@dashboard.route("/dashboard/trend_chart", methods=["GET", "POST"])
def trend_chart() -> Union[Callable[[dict], dict], Callable[[str, str], str]]:
    """Dashboard (trend chart – `Total Income`) route endpoint.

    Handles dashboard (trend chart – `Total Income`) template and logic.

    Args:
        GET: /trend_chart
        POST: /trend_chart

    Returns:
        Union[Callable[[dict], dict], Callable[[str, str], str]]: Json payload of
            chart dimensions and x-axis labels or HTML template for `Total Income` on /dashboard.
    """
    if request.method == "POST":
        # retrieve all relevant objects from database, in Bookings and Staycations
        bookings = Booking.objects.all()

        # compute daily booking income by hotels
        daily_booking_income_by_hotel = _compute_daily_booking_income(bookings)
        new_chart = Chart(dates=None, start_date=None, end_date=None, data=None).save()
        # insert daily booking income by hotels into chart
        new_chart.insert_data(daily_booking_income_by_hotel)
        # retrieve the recent updated chart object from database
        chart_object = Chart.objects(id=new_chart.id).first()
        # process chart dimensions and x-axis labels
        (
            chart_dimension,
            x_labels,
        ) = chart_object.prepare_chart_dimension_and_label()
        # POST request the chart dimension and x-axis labels
        # via AJAX to generate chart on the canvas for the dashboard
        return jsonify({"chartDim": chart_dimension, "labels": x_labels})
    # return dashboard (trend_chart) page by default if GET request
    return render_template("trend_chart.html", panel="Dashboard")


@dashboard.route("/dashboard/bar_chart_by_user", methods=["GET", "POST"])
def bar_chart_by_user() -> Union[Callable[[str, str], str], Callable[[dict], dict]]:
    """Dashboard (bar chart – `Due by User`) route endpoint.

    Handles dashboard (bar chart – `Due by User`)  template and logic.

    Args:
        GET:  /bar_chart.html
        POST: /bar_chart.html

    Returns:
        Union[Callable[[str, str], str], Callable[[dict], dict]]: Json payload of
            chart dimensions and x-axis labels or HTML template for `Due by User` on /dashboard.
    """
    # retrieve all available user names, excluding Admin
    user_names = [user.name for user in User.objects.all() if user.name != "Admin"]
    # retrieve selected value from select tag on `Due By User`
    target_user = request.form.get("username")
    if request.method == "GET":
        return render_template(
            "bar_chart.html",
            user_names=user_names,
            card_header="Due Per User",
            panel="Dashboard",
        )
    elif request.method == "POST":
        # retrieve all bookings made by the target user
        bookings_due_by_user = _compute_booking_due_by("user", target_user)
        # generate BarChart object for plotting
        new_chart = BarChart(data=None).save()
        # insert daily booking income by hotels into chart
        new_chart.insert_data(bookings_due_by_user, target_user)
        # retrieve the recent updated chart object from database
        chart_object = BarChart.objects(id=new_chart.id).first()
        # process chart dimensions and x-axis labels
        (
            chart_dimension,
            x_labels,
        ) = chart_object.prepare_chart_dimension_and_label()
        # POST data for charting with chart.js
        return jsonify(
            {
                "chartDim": chart_dimension,
                "labels": x_labels,
                "user_name": target_user,
            }
        )


@dashboard.route("/dashboard/bar_chart_by_hotel", methods=["GET", "POST"])
def bar_chart_by_hotel() -> Union[Callable[[str, str], str], Callable[[dict], dict]]:
    """Dashboard (bar chart – `Due by Hotel`) route endpoint.

    Handles dashboard (bar chart – `Due by Hotel`)  template and logic.

    Args:
        GET: /bar_chart.html
        POST: /bar_chart.html

    Returns:
        Union[Callable[[str, str], str], Callable[[dict], dict]]: Json payload of
            chart dimensions and x-axis labels or HTML template for `Due by Hotel` on /dashboard
    """
    # retrieve all available hotel names
    hotel_names = [staycation.hotel_name for staycation in Staycation.objects.all()]
    # retrieve selected value from select tag on `Due By Hotel`
    target_hotel = request.form.get("hotelname")
    if request.method == "GET":
        return render_template(
            "bar_chart.html",
            hotel_names=hotel_names,
            card_header="Due Per Hotel",
            panel="Dashboard",
        )
    elif request.method == "POST":
        # retrieve all bookings made by the target hotel
        bookings_due_by_hotel = _compute_booking_due_by("hotel", target_hotel)
        # generate BarChart object for plotting
        new_chart = BarChart(data=None).save()
        # insert daily booking income by hotels into chart
        new_chart.insert_data(bookings_due_by_hotel, target_hotel)
        # retrieve the recent updated chart object from database
        chart_object = BarChart.objects(id=new_chart.id).first()
        # process chart dimensions and x-axis labels
        (
            chart_dimension,
            x_labels,
        ) = chart_object.prepare_chart_dimension_and_label()
        # POST data for charting with chart.js
        return jsonify(
            {
                "chartDim": chart_dimension,
                "labels": x_labels,
                "hotel_name": target_hotel,
            }
        )


@dashboard.route("/dashboard")
@login_required
def render_dashboard() -> Callable[[Callable[[str], str]], Response]:
    """Dashboard route endpoint.

    Returns:
        Callable[[Callable[[str], str]], Response]: Redirected to URL for `trend_chart` endpoint and template.
    """
    return redirect(url_for("dashboard.trend_chart"))
