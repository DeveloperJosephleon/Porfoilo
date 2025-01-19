from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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

    # Process the form data (e.g., log it, save it to a database, or send an email)
    print(f"Message from {fullname} ({email}): {message}")

    # Respond with success
    return jsonify({"message": "Your message has been sent successfully!"}), 200


app.config.from_object('config.Config')

if __name__ == '__main__':
    app.run(debug=True)





