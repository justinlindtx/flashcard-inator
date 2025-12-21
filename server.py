# include flask app, set up db connection, register GET/POST routes
# handler functions go in routes.py??

from flask import Flask, render_template, redirect, session, request, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, FlashcardSet

app = Flask(__name__)
app.secret_key = 'unguessable-key'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

def login_required(view):
	@wraps(view)
	def wrapped_view(*args, **kwargs):
		if not session.get('user_id'):
			return redirect(url_for('index'))
		return view(*args, **kwargs)
	return wrapped_view

@app.route('/')
def index():
	# Redirect to main app if user is logged in
	if session.get('user_id'):
		return redirect(url_for('app_page'))
	# Otherwise display the login screen
	return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
	username = request.form.get('username')
	password = request.form.get('password')
	user = User.query.filter_by(username=username).first()
	if user and check_password_hash(user.password, password):
		session['user_id'] = user.id
		return redirect(url_for('app_page'))
	return render_template('login.html', error="Incorrect username/password combo")

@app.route('/register', methods=["POST","GET"])
def register():
	if request.method == "GET":
		return render_template('register.html')
	username = request.form.get('username')
	password = request.form.get('password')
	if User.query.filter_by(username=username).first():
		return render_template('register.html', error="Username already taken")
	user = User(username=username, password=generate_password_hash(password))
	db.session.add(user)
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/app')
@login_required
def app_page():
	user_id = session.get('user_id')
	sets = FlashcardSet.query.filter_by(user_id=user_id).order_by(FlashcardSet.last_updated).all()
	return render_template('app.html', sets=sets)

@app.route('/buildset')
@login_required
def build_set():
	return render_template('buildset.html')

@app.route('/create', methods=["POST"])
def create_set():
	user_id = session.get('user_id')
	title = request.form.get('set_title')
	description = request.form.get('set_desc')
	set = FlashcardSet(user_id=user_id, title=title, description=description)
	db.session.add(set)
	db.session.commit()
	return redirect(url_for('app_page'))

@app.route('/logout', methods=["POST"])
def logout():
	session.clear()
	return redirect(url_for('index'))

if __name__ == "__main__":
	with app.app_context():
		db.create_all()

	app.run(host="0.0.0.0", port=80, debug=True)