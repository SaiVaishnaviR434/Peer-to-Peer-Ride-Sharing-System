# Peer-to-Peer-Ride-Sharing-System
The Peer-to-Peer Ride Sharing System is a web-based application developed using Python and Flask . It connects two types of users—ride sharers and ride seekers—facilitating carpooling in a secure and efficient manner. The system ensures user safety and simplifies cost-sharing, encouraging eco-friendly transportation solutions.

Features:
User Registration and Login:
Users can register with personal details and login securely.
Role-Based Functionality:
Ride Sharer (User1): Can create a ride by providing trip details, including destination, available seats, and fare.
Ride Seeker (User2): Can search for rides to their destination, view ride details, and join a suitable ride.
Secure Ride Sharing:
Female users can opt for female-only co-passengers for enhanced safety.
Drivers are verified by uploading original documents.
Ride Details and History:
Users can view ride histories, including joined rides (User2) and shared rides (User1).
Chat Communication:
Integrated chat feature enables ride seekers to communicate with the sharer for trip coordination.
Responsive Frontend:
User-friendly interface with animations and navigation for a seamless experience.
Technologies Used
Frontend: HTML, CSS, JavaScript
Backend: Python (Flask)
Database: Firebase (or an alternative database)
Development Tools: Visual Studio Code
File Structure
style.css: Styles for the application, including animations and navigation.
templates/: Contains HTML templates for the application (e.g., login, registration, home, ride search, etc.).
app.py: Main application file that handles routing and logic.
firebase_config.py: Configuration file for connecting Firebase.
firebase-key.json: Contains Firebase credentials for secure database access.
