from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class MyForm(FlaskForm):
    Blog_title = StringField('Enter the Blog Title', validators=[DataRequired()])
    Blog_Subtitle = StringField('Blog Subtitle', validators=[DataRequired()])
    Background_url = StringField("Url for the Bg", validators=[DataRequired()])
    ckeditor = CKEditorField('Blog Content', render_kw={'class': 'ckeditor'})
    submit_field = SubmitField('Submit')

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Show Me')

class Login(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Let Me In! ')

class CommentForm(FlaskForm):
    comments = CKEditorField('Blog Content', render_kw={'class': 'ckeditor'})
    submit = SubmitField('Post')


    