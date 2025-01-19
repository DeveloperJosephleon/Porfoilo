from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.fullname}>'

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')

# Add the Contact model to the admin panel
admin.add_view(ModelView(Contact, db.session))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    # Get JSON data from the request
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

        # Respond with success
        return jsonify({"message": "Your message has been saved successfully!"}), 200
    except Exception as e:
        print(f"Error saving message: {e}")
        return jsonify({"error": "An error occurred while saving your message."}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback any transactions if an error happens
    return render_template('500.html'), 500



if __name__ == '__main__':
    # Create the database tables (if they don't already exist)
    with app.app_context():
        db.create_all()

    app.run(debug=True)
