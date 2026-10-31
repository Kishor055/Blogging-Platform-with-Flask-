from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms.fields.choices import SelectChoice
from wtforms import SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=180)])
    excerpt = TextAreaField("Short summary", validators=[Optional(), Length(max=320)])
    content = TextAreaField("Article", validators=[DataRequired(), Length(min=20)])
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    tag_ids = SelectMultipleField("Tags", coerce=int, validators=[Optional()])
    featured_image = FileField(
        "Featured image",
        validators=[Optional(), FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Choose a supported image.")],
    )
    status = SelectField(
        "Visibility",
        choices=[
            SelectChoice("draft", "Save as draft"),
            SelectChoice("published", "Publish now"),
            SelectChoice("scheduled", "Schedule publishing"),
        ],
    )
    scheduled_local = StringField("Publish date and time")
    schedule_timezone = StringField("Your timezone", default="UTC", validators=[Optional(), Length(max=64)])
    submit = SubmitField("Save article")

    def set_choices(self, categories, tags):
        self.category_id.choices = [SelectChoice("0", "No category")] + [
            SelectChoice(str(item.id), item.name) for item in categories
        ]
        self.tag_ids.choices = [SelectChoice(str(item.id), item.name) for item in tags]


class CommentForm(FlaskForm):
    content = TextAreaField("Your comment", validators=[DataRequired(), Length(min=2, max=2000)])
    submit = SubmitField("Post comment")
