from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, InputRequired, Length


class RegForm(FlaskForm):
    """Form validation class for Registration Form.
    `RegForm` inherits from FlaskForm that allow us to represent a collection of fields, which can be access on the form dictionary-style or attribute style.

    The form will later be pass to the specific template and rendered in HTML that allow users to insert input.

    By default, session is secured with csrf protection. A series of validators are also defined to
    put restriction on the field to be met based on the user's input.

    If validation fails, the form will fail and corresponding error message will be displayed.
    """

    # creating a form input for string input with a required validator
    # based on user's email input, where the max length is set to 30
    # this field is also compulsory to be filled
    email = StringField(
        "Email",
        validators=[
            InputRequired(),
            Email(message="Invalid email address"),
            Length(max=30),
        ],
    )
    # create a form input for password with required validator
    # minimum length of 5 characters, to max 50 characters is enforced
    # this field is also compulsory to be filled
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=5, max=50)]
    )
    # create a form input for string input with a required validator
    # based on user's nam input
    name = StringField("Name")


class BookingForm(FlaskForm):
    """Form validation class for Booking Form.

    By default, session is secured with csrf protection.
    """

    # create a form input for date input required for booking
    # this field requires data to be selected from the datepicker
    date = DateField(
        "Check-in Date",
        format="%Y-%m-%d",
        validators=([DataRequired()]),
    )
