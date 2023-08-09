from flask import Flask, redirect, render_template, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import UserLogInForm, UserRegisterationForm, CreatePostForm, CommentForm
from flask_gravatar import Gravatar
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False,
                    force_lower=False, use_ssl=False, base_url=None)
print(os.getenv("SECRET_KEY"))
# DB Connection  'sqlite:///blog.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# The view in case the user is not authenticated
login_manager.login_view = "login"

# DB Configuration


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship('Posts', back_populates='author')
    comments = relationship('Comments', back_populates='comment_author')


class Posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship('User', back_populates='posts')
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    p_date = db.Column(db.String(100), nullable=False)
    body = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship('Comments', back_populates='parent_post')


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship('Posts', back_populates='comments')
    comment_author = relationship('User', back_populates='comments')
    text = db.Column(db.Text, nullable=False)

# Execute Once to build DB tables
# with app.app_context():
#     db.create_all()


@app.route('/')
def home():
    posts = Posts.query.all()
    print(current_user)
    return render_template('index.html', posts=posts, current_user=current_user)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    reg_form = UserRegisterationForm()
    if reg_form.validate_on_submit():
        if User.query.filter_by(email=reg_form.email.data).first():
            # Someone registered with this email
            flash("You have registered with this email please log in")
            return redirect(url_for('login'))

        user_password = generate_password_hash(
            reg_form.password.data, method="pbkdf2:sha256", salt_length=8)
        user = User(email=reg_form.email.data,
                    password=user_password, name=reg_form.name.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))

    return render_template('register.html', form=reg_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    log_form = UserLogInForm()
    if log_form.validate_on_submit():
        email = log_form.email.data
        password = log_form.password.data
        user = User.query.filter_by(email=email).first()
        # Check if email exist
        if not user:
            flash("Email Not found, Please try again or register ")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Incorrect password')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', form=log_form)


@app.route('/logout')
def log_out():
    logout_user()
    return redirect(url_for('home'))


@app.route('/create_post', methods=['POST', 'GET'])
def create_post():
    post_form = CreatePostForm()

    if post_form.validate_on_submit():
        new_post = Posts(title=post_form.title.data, author=current_user,
                         subtitle=post_form.subtitle.data,
                         p_date=date.today().strftime("%B %d, %Y"),
                         body=post_form.body.data,
                         img_url=post_form.img_url.data)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('new_post.html', form=post_form, user=current_user)


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def show_post(post_id):
    post = Posts.query.get(post_id)
    comments = Comments.query.filter_by(post_id=post_id)
    form = CommentForm()
    logged_in = current_user.is_authenticated
    if logged_in:
        print("logged_in")
    # print(post.img_url)
    if form.validate_on_submit():
        new_comment = Comments(post_id=post_id,
                               author_id=current_user.id,
                               parent_post=post,
                               comment_author=current_user,
                               text=form.comment.data)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template('post.html', post=post, comments=comments, form=form, logged_in=logged_in)


@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Posts.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
@login_required
def edit_post(post_id):
    post = Posts.query.get(post_id)
    edit_form = CreatePostForm(obj=post)

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))

    return render_template('new_post.html', form=edit_form, user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
