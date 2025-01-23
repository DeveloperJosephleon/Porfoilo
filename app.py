from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.form import FileUploadField

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')  # Load configurations from config.py

# Initialize the database
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

# Configure upload directory and allowed extensions
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'
app.config['UPLOADED_IMAGES_URL'] = '/static/uploads/'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# Define the User model for admin users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<BlogPost {self.title}>'

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
    form_extra_fields = {
        'image': FileUploadField(
            'Image',
            base_path='static/uploads',
        )
    }

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

    def on_model_change(self, form, model, is_created):
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and images.file_allowed(image_file, image_file.filename):
                model.image = images.save(image_file)
            else:
                raise ValueError("Invalid image file.")

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(SecureModelView(Contact, db.session))
admin.add_view(SecureModelView(BlogPost, db.session))

# Routes
@app.route('/')
def home():
    posts = BlogPost.query.order_by(BlogPost.date.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    message = data.get('message')

    if not fullname or not email or not message:
        return jsonify({"error": "All fields are required!"}), 400

    try:
        new_contact = Contact(fullname=fullname, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"message": "Your message has been saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while saving your message."}), 500

# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('admin.index'))

#         return render_template('admin_login.html', error="Invalid credentials")
#     return render_template('admin_login.html')


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
    logout_user()
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()

#         if not User.query.filter_by(username='admin').first():
#             admin_user = User(username='admin', password=generate_password_hash('securepassword'))
#             db.session.add(admin_user)
#             db.session.commit()

#     app.run(debug=True)


# if __name__ == '__main__':
#     with app.app_context():
#         try:
#             # Create all tables in the database
#             db.create_all()
#             print("Database tables created successfully.")

#             # Check if the admin user exists, and create one if not
#             if not User.query.filter_by(username='admin').first():
#                 admin_user = User(username='admin', password=generate_password_hash('securepassword'))
#                 db.session.add(admin_user)
#                 db.session.commit()
#                 print("Admin user created with default credentials.")
#             else:
#                 print("Admin user already exists.")

#         except Exception as e:
#             print(f"Error initializing the database: {e}")

#     # Run the Flask app
#     app.run(debug=True)


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
	

