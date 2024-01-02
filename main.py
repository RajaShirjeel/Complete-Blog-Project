from __future__ import annotations
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from forms import MyForm, RegisterForm, Login, CommentForm
import datetime
import secrets
from sqlalchemy.orm import relationship




app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

login_manager = LoginManager()
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app) 
login_manager.init_app(app)  


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    
    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    
    #Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
   
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    comments = relationship("Comment", back_populates='parent_post')


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")

    text = db.Column(db.Text, nullable=False)





with app.app_context():
    db.create_all()

def admin_only(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id !=1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_func



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def get_all_posts():
    results = db.session.execute(db.select(BlogPost))
    posts = results.scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route('/post/<post_id>', methods=['POST','GET'])
def show_post(post_id):
    form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to register or login to comment")
            return redirect(url_for('login'))
        new_comment = Comment(
            text = form.comments.data,
            comment_author = current_user,
            parent_post = requested_post
        )
        db.session.add(new_comment)
        db.session.commit()  
    return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/new-post', methods=['POST','GET'])
@admin_only
def new_post():
    form = MyForm()
    if form.validate_on_submit():
        today = datetime.datetime.now()
        today = today.strftime('%B %d, %Y')
        new_entry = BlogPost(
            title = form.Blog_title.data,
            subtitle = form.Blog_Subtitle.data,
            date = today,
            body = form.ckeditor.data,
            author = current_user,
            img_url = form.Background_url.data
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('show_post', post_id=new_entry.id))
    return render_template('make-post.html', form=form)


@app.route('/edit-post/<post_id>', methods=['GET', 'POST'])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = MyForm(
    Blog_title = post.title,
    Blog_subtitle = post.subtitle,
    Background_url = post.img_url,
    Author_name = post.author.name,
    ckeditor = post.body
)
    if form.validate_on_submit():
        post.title = form.Blog_title.data
        post.subtitle = form.Blog_Subtitle.data
        post.author =  current_user
        post.img_url = form.Background_url.data
        post.body = form.ckeditor.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    
    return render_template('make-post.html', is_edit=True, form=form)


@app.route('/delete-post/<post_id>')
@admin_only
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id )
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            password = generate_password_hash(form.password.data, salt_length=10)
            new_user = User(
                email = form.email.data,
                password = password,
                name = form.name.data
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts')) 
        else:
            flash('Email Already exists, Please Login')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash('No Email Found!')
            return redirect(url_for('login'))
        else:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Incorrect Password!')
                return redirect(url_for('login'))
        
    return render_template('login.html', form=form)

@app.route('/logout')
def log_out():
    logout_user()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True, port=5003)