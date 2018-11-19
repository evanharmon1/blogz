from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import cgi
from app import app, db
from models import User, Blog
from hashutils import make_salt, make_pw_hash, check_pw_hash


#Get paginated posts ordered from newest to oldest
def get_posts():
    return Blog.query.order_by("date desc").paginate(1, 2, False).items

def get_users():
    return User.query.all()

# Form validation for empty fields
def check_empty(field, name):
    if field == '':
        return f'You left the {name} field blank'
    else:
        return ''


# Require login for certain routes
@app.before_request
def require_login():
    allowed_routes = ['blog', 'index', 'login', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


# Homepage
@app.route('/')
def index():
    users = get_users()
    return render_template('index.html', users=users)


# Main blog page with blog posts
@app.route('/blog', methods=['GET'])
def blog():
    id = request.args.get('id', None)
    user_id = request.args.get('user-id', None)
    page = request.args.get('page', 1, type=int)

    if id:
        posts = Blog.query.filter_by(id=id).all()
        return render_template('blog.html', posts=posts)

    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id).order_by("date desc").paginate(page, 3, False)
        # Pagination
        current_page = page
        next_url = url_for('blog', page=posts.next_num) if posts.has_next else None
        prev_url = url_for('blog', page=posts.prev_num) if posts.has_prev else None
        return render_template('blog.html', posts=posts.items, next_url=next_url, prev_url=prev_url, pagination=posts.iter_pages(), current_page=current_page)

    # Pagination
    posts = Blog.query.order_by("date desc").paginate(page, 3, False)
    current_page = page
    next_url = url_for('blog', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('blog', page=posts.prev_num) if posts.has_prev else None
    return render_template('blog.html', posts=posts.items, next_url=next_url, prev_url=prev_url, pagination=posts.iter_pages(), current_page=current_page)


# Add a new post
@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    # When adding a new post from /newpost
    if request.method == 'POST':
        title = request.form.get('title', '')
        body = request.form.get('body', '')
    
        # Check for empty form fields with check_empty() function
        if not title or not body:
            return redirect(f"/newpost?title={title}&body={body}&title_error={check_empty(title, 'title')}&body_error={check_empty(body, 'body')}")

        # Add new post to database
        username = session['username']
        user = User.query.filter_by(username=username).first()
        new_post = Blog(title, user)
        new_post.body = body
        db.session.add(new_post)
        db.session.commit()

        # Load the newly created post in an individual page
        id = new_post.id
        posts = Blog.query.filter_by(id=id).all()
        return render_template('blog.html', posts=posts)

    # Get request from /newpost
    title = request.args.get('title', '')
    body = request.args.get('body', '')
    title_error = request.args.get('title_error', '')
    body_error = request.args.get('body_error', '')

    return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # Form validation for empty values with check_empty() function
        if not username or not password:
            return redirect(f"/login?username={username}&username_error={check_empty(username, 'username')}&password_error={check_empty(password, 'password')}")
        
        # Check for user in database
        user = User.query.filter_by(username=username).first()
        if user:
            if check_pw_hash(password, user.pw_hash):
                session['username'] = username
                return redirect('/newpost')
            if not check_pw_hash(password, user.pw_hash):
                password_error = 'Username found, but password not correct'
                return render_template('login.html', username=username, password_error=password_error)
        else:
            username_error = 'Username not found'
            return render_template('login.html', username=username, username_error=username_error)

    username = request.args.get('username', '')
    username_error = request.args.get('username_error', '')
    password_error = request.args.get('password_error', '')
    return render_template('login.html', username=username, username_error=username_error, password_error=password_error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        verify_password = request.form.get('verify_password', '')
        username_error = ''
        password_error = ''
        verify_password_error = ''
        user = User.query.filter_by(username=username).first()

        # # Form validation: existing user, field length, empty fields, & verify password field match
        if user:
            if username == user.username:
                username_error = 'User already exists. Please choose another username'
                return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')
        if not (3 <= len(username) <= 25):
            username_error = 'Username must be between 3 and 25 characters'
            return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')
        if not (3 <= len(password) <= 25):
            password_error = 'Password must be between 3 and 25 characters'
            return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')
        if not username or not password or not verify_password:
            return redirect(f"/signup?username={username}&username_error={check_empty(username, 'username')}&password_error={check_empty(password, 'password')}&verify_password_error={check_empty(verify_password, 'verify password')}")
        if password != verify_password:
            verify_password_error = 'Your passwords do not match'
            return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')

        new_user = User(username, make_pw_hash(password))
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')

    username = request.args.get('username', '')
    username_error = request.args.get('username_error', '')
    password_error = request.args.get('password_error', '')
    verify_password_error = request.args.get('verify_password_error', '')
    return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_password_error=verify_password_error)


if __name__ == "__main__":
    app.run()
