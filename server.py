# --- Existing Imports ---
from flask import Flask, render_template, request, redirect
import smtplib
import os # Keeping os import in case it's needed elsewhere later
import datetime
from email.message import EmailMessage
# from dotenv import load_dotenv # Removed dotenv import
import pymongo # For MongoDB

# --- Load Environment Variables REMOVED ---

app = Flask(__name__)

# --- MongoDB Connection Setup ---
# --- Using Hardcoded Connection String (EXTREMELY INSECURE!) ---
mongo_uri = "mongodb+srv://erezamsalem:GOCnVwpWqOEisakH@my-personal-site.htpramq.mongodb.net/?retryWrites=true&w=majority&appName=my-personal-site"
# ---
db = None # Initialize db variable
if mongo_uri: # Check if string is present (it will be, unless deleted)
    try:
        client = pymongo.MongoClient(mongo_uri)
        # Select database name (replace 'my_contact_form_db' if needed)
        db_name = "my_contact_form_db"
        db = client[db_name]
        db.command('ping') # Test connection
        print(f"Successfully connected to MongoDB database: {db_name}!")
    except Exception as e:
        print(f"ERROR: Could not connect to MongoDB using the provided string: {e}")
        # Application can continue but saving to DB will fail
else:
     print("ERROR: MongoDB connection string is missing in the code.")


@app.route('/')
def my_home():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    safe_pages = ['index.html', 'works.html', 'about.html', 'contact.html', 'thankyou.html']
    if page_name in safe_pages:
        return render_template(page_name)
    else:
        return "Page not found", 404

# --- Function to save data to MongoDB ---
def save_to_mongo(data):
    if db is None: # Check if connection failed during startup
        print("ERROR: MongoDB connection not available. Cannot save data.")
        return False
    try:
        contacts_collection = db.contacts # Use/create 'contacts' collection
        document = {
            'email': data.get('email'),
            'subject': data.get('subject'),
            'message': data.get('message'),
            'submitted_at': datetime.datetime.utcnow() # Add a timestamp
        }
        insert_result = contacts_collection.insert_one(document)
        print(f"Data saved to MongoDB collection 'contacts' with id: {insert_result.inserted_id}")
        return True
    except Exception as e:
        print(f"ERROR: Could not save data to MongoDB: {e}")
        return False

# --- Email Sending Function (Uses Hardcoded Credentials) ---
def send_email(data):
    # --- Using Hardcoded Credentials (EXTREMELY INSECURE!) ---
    gmx_login_email = "erezamsalem@gmx.com"
    gmx_password = "Javascript2024@@"  # <-- Your GMX password/App Password

    sender_email = data.get("email")
    subject = data.get("subject", "No Subject")
    message_body = data.get("message", "")

    if not sender_email:
        print("Error: Visitor did not provide an email address in the form.")
        return False

    msg = EmailMessage()
    msg['Subject'] = f"Copy of your Contact Form Submission: {subject}"
    msg['From'] = gmx_login_email
    msg['To'] = sender_email
    msg.set_content(f"Thank you for contacting us.\n\nHere is a copy of your message:\n\nFrom: {sender_email}\nSubject: {subject}\n\nMessage:\n{message_body}")

    try:
        print(f"Connecting to smtp.gmx.com:587...")
        server = smtplib.SMTP('smtp.gmx.com', 587)
        server.starttls()
        print(f"Logging in as {gmx_login_email}...")
        # Login using the hardcoded variables
        server.login(gmx_login_email, gmx_password)
        print(f"Sending email to {sender_email}...")
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"SMTP Authentication Error: Could not log in with {gmx_login_email}.")
        print("Please double-check the hardcoded password (or App Password if using 2FA) and GMX account settings.")
        return False
    except Exception as e:
        print(f"Error sending email via GMX to {sender_email}: {e}")
        return False

# --- Modified submit_form route ---
@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            print(f"Received form data: {data}")

            print("Attempting to save data to MongoDB...")
            mongo_saved_ok = save_to_mongo(data)

            if mongo_saved_ok:
                print("Attempting to send email notification to visitor...")
                email_sent_ok = send_email(data)
                if not email_sent_ok:
                    print("Warning: Data saved to DB, but confirmation email failed to send.")
                return redirect('/thankyou.html')
            else:
                 return 'Failed to save your message to the database. Please try again later.'

        except Exception as e:
            print(f"Error processing form submission: {e}")
            return 'An unexpected error occurred while processing your form.'
    else:
        return redirect('/contact.html')

# if __name__ == '__main__':
#     app.run(debug=True)