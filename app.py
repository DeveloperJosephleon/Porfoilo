from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')  # Load configurations from config.py

# Initialize the database
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'  # Redirect unauthorized users to admin login page

# Define the User model for admin users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.fullname}>'

# Secure Flask-Admin by restricting access to logged-in admin users
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  # Only allow logged-in users to access admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))  # Redirect unauthorized users to login page

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(SecureModelView(Contact, db.session))

# Routes
@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    """Handle form submissions."""
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    message = data.get('message')

    # Validate the data
    if not fullname or not email or not message:
        return jsonify({"error": "All fields are required!"}), 400

    try:
        # Save the data to the database
        new_contact = Contact(fullname=fullname, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"message": "Your message has been saved successfully!"}), 200
    except Exception as e:
        print(f"Error saving message: {e}")
        return jsonify({"error": "An error occurred while saving your message."}), 500

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user (hardcoded for now, replace with hashed password check)
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Replace with `check_password_hash` in production
            login_user(user)
            return redirect(url_for('admin.index'))  # Redirect to Flask-Admin panel

        return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin_logout')
@login_required
def admin_logout():
    """Log out the admin."""
    logout_user()
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()  # Rollback any failed transactions
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()

        # Add a default admin user (only if no admin exists)
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='securepassword')  # Replace with hashed password
            db.session.add(admin_user)
            db.session.commit()

    app.run(debug=True)
