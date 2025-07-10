from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DecimalField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
import re

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(max=20)])
    nid_number = StringField('NID Number', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=255)])
    role = SelectField('Role', choices=[('user', 'User'), ('service_provider', 'Service Provider')], validators=[DataRequired()])

    def validate_contact_number(self, field):
        if not re.match(r'^[\d\-\+\(\)\s]+$', field.data):
            raise ValidationError('Invalid contact number format.')

    def validate_password(self, field):
        if len(field.data) < 6:
            raise ValidationError('Password must be at least 6 characters long.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class ServiceForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    service_name = StringField('Service Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description')
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    location = StringField('Location', validators=[Length(max=255)])

class BookingForm(FlaskForm):
    service_date = DateTimeField('Service Date', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[('bkash', 'bKash'), ('nagad', 'Nagad'), ('card', 'Card')], validators=[DataRequired()])

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment')

class SupportTicketForm(FlaskForm):
    issue_description = TextAreaField('Issue Description', validators=[DataRequired()])

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(max=20)])
    age = IntegerField('Age', validators=[NumberRange(min=1, max=120)])
    profession = StringField('Profession', validators=[Length(max=100)])
    address = TextAreaField('Address')
    professional_description = TextAreaField('Professional Description')
    expertise = StringField('Expertise', validators=[Length(max=255)])
    preferred_locations = StringField('Preferred Locations')
    portfolio_url = StringField('Portfolio URL', validators=[Length(max=255)])

    def validate_contact_number(self, field):
        if not re.match(r'^[\d\-\+\(\)\s]+$', field.data):
            raise ValidationError('Invalid contact number format.')

