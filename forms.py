from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditorField

class UserLogInForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class UserRegisterationForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    submit = SubmitField("Register")
    
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title:", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL:", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
    
class CommentForm(FlaskForm):
    comment = CKEditorField("Your Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")