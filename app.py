from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import firebase_admin
import pyrebase
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from firebase_admin import credentials, db
from firebase_config import firebaseConfig
# Initialize Pyrebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth_pyrebase = firebase.auth()
db_pyrebase = firebase.database()
# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'abcdefghijkl'  # Required for session management
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-key.json")  # Replace with your Firebase Admin SDK JSON key
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://peer2peer-ride-sharing-system-default-rtdb.firebaseio.com"  # Replace with your Firebase database URL
})
ride_data_ref = db.reference("rides")
user_data_ref = db.reference("users")
def save_file(file):
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return filepath
    return None
@app.route('/')  # Home page redirects to login if not logged in
def home():
    if 'user_id' in session:  # Check if the user is logged in
        return redirect(url_for('profile'))
    return redirect(url_for('register')) 
# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        confirm_password=request.form['confirm_password']
        if password!=confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))
        ref=db.reference('users')
        users=ref.get()
        if users:
            for user_id, user_data in users.items():
                if user_data.get('email') == email:
                    flash("User already exists with this email!", "error")
                    return redirect(url_for('register'))

        # Add new user to the database
        ref.push({
            'user_id':user_id,
            'name':name,
            'email': email,
            'age':age,
            'gender':gender,
            'password': password  # Note: Hash passwords for security in real applications
        })
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
  return render_template('register.html')
 
# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check user credentials
        ref = db.reference('users')
        users=ref.get()
        if users:
            for user_id, user_data in users.items():
                # Check if the email and password match
                if user_data.get('email') == email and user_data.get('password') == password:
                    flash("Login successful!", "success")
                    return redirect(url_for('home'))  # Redirect to home or dashboard page
        flash("Invalid email or password!", "error")
        return redirect(url_for('profile'))

    return render_template('login.html')
        
# Profile Page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:  # Redirect to login if user is not authenticated
        return redirect(url_for('login'))

    # Handle Book Ride and Publish Ride functionality here
    if request.method == 'POST':
        if request.form.get('leaving_from'):  # Book a Ride form
            # Process Book a Ride details
            leaving_from = request.form['leaving_from']
            going_to = request.form['going_to']
            ride_date = request.form['ride_date']
            person_count = request.form['person_count']
            # Store ride details in the database (implement as needed)
            flash('Ride search submitted!', 'success')

        elif request.form.get('Source'):  # Publish a Ride form
            # Process Publish a Ride details
            source = request.form['Source']
            destination = request.form['destination']
            ride_date = request.form['ride_date']
            available_seats = request.form['available_seats']
            ride_fare = request.form['ride_fare']
            # Store ride details in the database (implement as needed)
            flash('Ride published successfully!', 'success')

    return render_template('profile.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))
# Driver Details Page
@app.route('/driver_details', methods=['GET', 'POST'])
def driver_details():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            name = request.form['name']
            contact_number = request.form['contact_number']
            car_details = request.form['car_details']
            additional_notes = request.form.get('additional_notes', '')
            address_proof = save_file(request.files['address_proof'])
            driving_license = save_file(request.files['driving_license'])
            vehicle_document = save_file(request.files['vehicle_document'])
            vehicle_insurance = save_file(request.files['vehicle_insurance'])
            driver_data = {
                "name": name,
                "contact_number": contact_number,
                "car_details": car_details,
                "additional_notes": additional_notes,
                "address_proof": address_proof,
                "driving_license": driving_license,
                "vehicle_document": vehicle_document,
                "vehicle_insurance": vehicle_insurance,
            }
            db.reference(f"drivers/{session['user']['uid']}").set(driver_data)
            return redirect(url_for('ride_published'))
        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('driver_details'))
    return render_template('driver_details.html')
@app.route('/publish', methods=['POST'])
def publish():
    if 'user_id' in session:
        user_id = session['user_id']
        source = request.form.get('source')
        destination = request.form.get('destination')
        ride_fare = request.form.get('ride_fare')

        if source and destination:
            ride_data = {
                'user_id': user_id,
                'source': source.lower(),
                'destination': destination.lower(),
                'ride_fare': ride_fare,
                'status': 'available'
            }
            
            # Push to Firebase and log the result
            result = db.child("rides").push(ride_data)
            print("Ride data pushed to Firebase:", result)
            return jsonify({"message": "Ride shared successfully!"})
        else:
            return jsonify({"error": "Source and destination are required!"})
    else:
        return jsonify({"error": "Please log in to publish a ride!"})
@app.route('/search', methods=['POST'])
def search():
    if 'user_id' in session:
        user_id = session['user_id']
        source = request.form.get('source')
        destination = request.form.get('destination')
        
        if source and destination:
            # Query Firebase for matching rides
            rides = db.child("rides").get().val()
            matching_rides = []

            if rides:
                for ride_id, ride in rides.items():
                    # Check if the source and destination match (case insensitive)
                    if (ride['source'] == source.lower() and
                        ride['destination'] == destination.lower() and
                        ride['status'] == 'available' and
                        ride['user_id'] != user_id):  # Exclude own rides
                        matching_rides.append({
                            "ride_id": ride_id,
                            "user_id": ride['user_id'],
                            "ride_fare": ride['ride_fare'],
                            "document_url": ride.get('document_url')
                        })

            if matching_rides:
                return jsonify({"rides": matching_rides})
            else:
                return jsonify({"message": "No available rides found!"})
        else:
            return jsonify({"error": "Source and destination are required!"})
    else:
        return jsonify({"error": "Please log in to search for rides!"})

@app.route('/ride_published')
def ride_published():
    if 'user' not in session:
        return redirect(url_for('login'))
    return "Your ride has been successfully published!"
@app.route('/available_rides', methods=['POST'])
def available_rides():
    destination = request.form['going_to'].lower()

    # Retrieve all rides from the 'rides' reference
    rides = ride_data_ref.get()

    available_rides = []
    if rides:  # Check if there are any rides
        for ride_id, ride_details in rides.items():
            if ride_details.get('destination', '').lower() == destination:
                available_rides.append({
                    'source': ride_details.get('source', 'Unknown'),
                    'destination': ride_details.get('destination', 'Unknown'),
                    'date': ride_details.get('date', 'Unknown'),
                    'fare': ride_details.get('fare', 'N/A'),  # Use 'N/A' if fare is missing
                    'available_seats': ride_details.get('available_seats', 'Unknown')
                })

    return render_template('available_rides.html', available_rides=available_rides)


@app.route('/join_ride', methods=['POST'])
def join_ride():
    if 'user' not in session:
        return redirect(url_for('login'))

    ride_id = request.form['ride_id']
    user_id = session['user']

    # Fetch User1 details
    user1_details = user_data_ref.child(user_id).get()
    if not user1_details:
        return "User not found", 404

    # Add User1's request to the ride
    ride_data_ref.child(ride_id).child('user1_requests').child(user_id).set({
        'name': user1_details['name'],
        'contact': user1_details['contact'],
        'status': 'pending'
    })

    return redirect(url_for('available_rides'))
@app.route('/search_rides', methods=['POST'])
def search_rides():
    if 'user_id' in session:
        destination = request.form.get('destination').lower()
        gender = request.form.get('gender')
        low_cost = request.form.get('low_cost')
        near_from = request.form.get('near_from').lower() if request.form.get('near_from') else None

        # Fetch all rides from Firebase
        rides = db.child("rides").get().val()

        if rides:
            matching_rides = []
            for ride_id, ride in rides.items():
                # Check if destination matches
                if ride['destination'] == destination:
                    # Apply additional filters
                    if gender and gender != ride.get('gender', ''):
                        continue
                    if low_cost and int(ride['ride_fare']) > int(low_cost):
                        continue
                    if near_from and ride.get('source', '').lower() != near_from:
                        continue

                    matching_rides.append({
                        'ride_id': ride_id,
                        'source': ride['source'],
                        'destination': ride['destination'],
                        'ride_fare': ride['ride_fare'],
                        'gender': ride.get('gender', 'Not Specified')
                    })

            # Pass matching rides to the frontend
            if matching_rides:
                return render_template('results.html', rides=matching_rides)
            else:
                return render_template('results.html', message="No rides found matching your criteria.")

        else:
            return render_template('results.html', message="No rides available.")

    else:
        return jsonify({"error": "Please log in to search for rides!"})

@app.route('/my_rides', methods=['GET'])
def my_rides():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']
    rides = []

    # Fetch rides shared by the logged-in User2
    all_rides = ride_data_ref.get()
    if all_rides:
        for ride_id, ride_details in all_rides.items():
            if ride_details.get('user2_id') == user_id:
                ride_requests = ride_details.get('user1_requests', {})
                rides.append({
                    'ride_id': ride_id,
                    'destination': ride_details['destination'],
                    'requests': ride_requests
                })
    return render_template('my_rides.html', rides=rides)
@app.route('/respond_request', methods=['POST'])
def respond_request():
    if 'user' not in session:
        return redirect(url_for('login'))
    ride_id = request.form['ride_id']
    user_id = request.form['user_id']
    action = request.form['action']
    # Update the request status
    new_status = 'accepted' if action == 'accept' else 'rejected'
    ride_data_ref.child(ride_id).child('user1_requests').child(user_id).update({
        'status': new_status
    })
    return redirect(url_for('my_rides'))
if __name__ == '__main__':
    app.run(debug=True)