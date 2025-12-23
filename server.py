# include flask app, set up db connection, register GET/POST routes
# handler functions go in routes.py??

from flask import Flask, render_template, redirect, session, request, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, FlashcardSet, Flashcard

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
	if user and password and check_password_hash(user.password, password):
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
	user = User(username=username, password=generate_password_hash(password)) # type: ignore
	db.session.add(user)
	db.session.commit()
	return redirect(url_for('index'))

# Display the main page with a list of the user's flashcard sets
@app.route('/app')
@login_required
def app_page():
	user_id = session.get('user_id')
	session.pop('set_id', None)
	session.pop('set_title', None)
	session.pop('set_desc', None)
	sets = FlashcardSet.query.filter_by(user_id=user_id).order_by(FlashcardSet.last_updated.desc()).all()
	return render_template('app.html', sets=sets)

@app.route('/buildset')
@login_required
def buildset():
	set_id = session.get('set_id')
	set_title = session.get('set_title', '')
	set_desc = session.get('set_desc', '')
	cards = []
	if set_id:
		cards = Flashcard.query.filter_by(set_id=set_id).all()
	return render_template('buildset.html', cards=cards, 
						set_title=set_title, set_desc=set_desc)

@app.route('/add_element', methods=["POST"])
@login_required
def add_element():
	user_id = session.get('user_id')
	front_text = request.form.get('front_text')
	back_text = request.form.get('back_text')
	set_id = session.get('set_id')

	if set_id is None:
		# Create the set (first card)
		title = request.form.get('set_title')
		description = request.form.get('set_desc')
		set = FlashcardSet(user_id=user_id, title=title, description=description) # type: ignore
		db.session.add(set)
		db.session.flush()
		# Store set info in session
		session['set_id'] = set.id
		session['set_title'] = title
		session['set_desc'] = description
		set_id = set.id
	
	# Add the card to the set
	card = Flashcard(set_id=set_id, front_text=front_text, back_text=back_text) # type: ignore
	try:
		db.session.add(card)
		db.session.commit()
		return redirect(url_for('buildset'))
	except Exception as e:
		return f"ERROR: {e}"
	
@app.route('/delete_card/<int:id>')
@login_required
def delete_card(id:int):
	# Access control
	user_id = session.get('user_id')
	deleted_card = Flashcard.query.join(FlashcardSet).filter(
		Flashcard.id == id, FlashcardSet.user_id == user_id).first()
	if deleted_card is None:
		abort(404)
	
	# Delete database entry
	try:
		db.session.delete(deleted_card)
		db.session.commit()
		return redirect(url_for('buildset'))
	except Exception as e:
		return f"ERROR: {e}"

# Go back to main page and delete any in progress sets
@app.route('/cancel_set')
@login_required
def cancel_set():
	set_id = session.get('set_id')
	if set_id:
		canceled_set = FlashcardSet.query.get(set_id)
		db.session.delete(canceled_set)
		db.session.commit()
	return redirect(url_for('app_page'))

@app.route('/delete/<int:id>')
@login_required
def delete_set(id:int):
	# Access control
	user_id = session.get('user_id')
	deleted_set = FlashcardSet.query.filter_by(id=id, user_id=user_id).first()
	if deleted_set is None:
		abort(404)
	
	# Delete database entry
	try:
		db.session.delete(deleted_set)
		db.session.commit()
		return redirect(url_for('app_page'))
	except Exception as e:
		return f"ERROR: {e}"
	
@app.route('/study/<int:id>')
@login_required
def study_set(id:int):
	# Access control
	user_id = session.get('user_id')
	set = FlashcardSet.query.filter_by(id=id, user_id=user_id).first()
	if set is None:
		abort(404)
	# Return webpage
	return render_template('study.html', set=set)

@app.route('/edit-card/<int:id>', methods=["POST", "GET"])
@login_required
def edit_card(id:int):
	# Access control
	user_id = session.get('user_id')
	card = Flashcard.query.join(FlashcardSet).filter(
		Flashcard.id == id, FlashcardSet.user_id == user_id).first()
	if card is None:
		abort(404)

	# Return editing webpage
	if request.method == "GET":	
		return render_template('edit.html', card=card)
	# Save edit to database
	else:
		card.front_text = request.form.get('front_text');
		card.back_text = request.form.get('back_text');
		try:
			db.session.commit()
			return redirect(url_for('study_set', id=card.set_id))
		except Exception as e:
			return f"ERROR: {e}"

@app.route('/logout', methods=["POST"])
def logout():
	session.clear()
	return redirect(url_for('index'))

if __name__ == "__main__":
	with app.app_context():
		db.create_all()

	app.run(host="0.0.0.0", port=80, debug=True)