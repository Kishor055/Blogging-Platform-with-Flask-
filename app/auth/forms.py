from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, ValidationError

from app.extensions import db
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=40),
            Regexp(r"^[A-Za-z0-9_.-]+$", message="Use letters, numbers, dots, underscores, or hyphens."),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=254)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=10, max=128)])
    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Create account")

    def validate_username(self, field):
        username = field.data.strip()
        if User.query.filter(db.func.lower(User.username) == username.lower()).first():
            raise ValidationError("That username is already taken.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("An account already uses that email.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class ProfileForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=40),
            Regexp(r"^[A-Za-z0-9_.-]+$", message="Use letters, numbers, dots, underscores, or hyphens."),
        ],
    )
    bio = TextAreaField("About you", validators=[Length(max=500)])
    profile_image = FileField(
        "Profile image",
        validators=[Optional(), FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Choose a supported image.")],
    )
    submit = SubmitField("Save profile")

    def __init__(self, user_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id

    def validate_username(self, field):
        username = field.data.strip()
        existing = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        if existing and existing.id != self.user_id:
            raise ValidationError("That username is already taken.")
