import streamlit as st
import sqlite3
import bcrypt

# Database Setup
def init_db():
    conn = sqlite3.connect('egov_platform.db')
    c = conn.cursor()

    # Create Users table
    c.execute('''CREATE TABLE IF NOT EXISTS Users (
                  User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Username TEXT UNIQUE NOT NULL,
                  Password TEXT NOT NULL,
                  Email TEXT NOT NULL,
                  Role TEXT NOT NULL)''')

    # Create Citizen_Profile table
    c.execute('''CREATE TABLE IF NOT EXISTS Citizen_Profile (
                  Citizen_ID INTEGER PRIMARY KEY,
                  Name TEXT NOT NULL,
                  Date_of_Birth TEXT NOT NULL,
                  Address TEXT NOT NULL,
                  Phone_Number TEXT NOT NULL,
                  FOREIGN KEY(Citizen_ID) REFERENCES Users(User_ID))''')

    # Create Services table
    c.execute('''CREATE TABLE IF NOT EXISTS Services (
                  Service_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Service_Name TEXT NOT NULL,
                  Service_Description TEXT,
                  Category TEXT)''')

    # Create Service_Requests table
    c.execute('''CREATE TABLE IF NOT EXISTS Service_Requests (
                  Request_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Citizen_ID INTEGER,
                  Service_ID INTEGER,
                  Request_Status TEXT,
                  Request_Date TEXT,
                  FOREIGN KEY(Citizen_ID) REFERENCES Citizen_Profile(Citizen_ID),
                  FOREIGN KEY(Service_ID) REFERENCES Services(Service_ID))''')

    # Create Payments table
    c.execute('''CREATE TABLE IF NOT EXISTS Payments (
                  Payment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Request_ID INTEGER,
                  Payment_Method TEXT,
                  Payment_Date TEXT,
                  Payment_Amount REAL,
                  FOREIGN KEY(Request_ID) REFERENCES Service_Requests(Request_ID))''')

    # Create Documents table
    c.execute('''CREATE TABLE IF NOT EXISTS Documents (
                  Document_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Request_ID INTEGER,
                  Document_Type TEXT,
                  Document_Content BLOB,
                  FOREIGN KEY(Request_ID) REFERENCES Service_Requests(Request_ID))''')

    # Create Feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS Feedback (
                  Feedback_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Citizen_ID INTEGER,
                  Service_ID INTEGER,
                  Feedback_Rating INTEGER,
                  Feedback_Comment TEXT,
                  FOREIGN KEY(Citizen_ID) REFERENCES Citizen_Profile(Citizen_ID),
                  FOREIGN KEY(Service_ID) REFERENCES Services(Service_ID))''')

    # Create Analytics table
    c.execute('''CREATE TABLE IF NOT EXISTS Analytics (
                  Analytics_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                  Service_ID INTEGER,
                  Metric_Type TEXT,
                  Metric_Value REAL,
                  Date TEXT,
                  FOREIGN KEY(Service_ID) REFERENCES Services(Service_ID))''')

    conn.commit()
    conn.close()
# User Authentication
def create_user(username, password, email, role):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('egov_platform.db')
    c = conn.cursor()
    c.execute("INSERT INTO Users (Username, Password, Email, Role) VALUES (?, ?, ?, ?)", 
              (username, hashed_password, email, role))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('egov_platform.db')
    c = conn.cursor()
    c.execute("SELECT Password, Role FROM Users WHERE Username=?", (username,))
    data = c.fetchone()
    conn.close()
    if data:
        stored_password, role = data
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return role
    return None

# Authentication Pages
def login():
    st.subheader("Login to your account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = authenticate_user(username, password)
        if role:
            st.session_state["role"] = role
            st.session_state["username"] = username
            st.success(f"Logged in as {role}")
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")

def register():
    st.subheader("Register a new account")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    email = st.text_input("Enter your Email")
    role = st.selectbox("Select Role", ["Citizen", "Service Officer", "Government Administrator"])
    if st.button("Register"):
        create_user(username, password, email, role)
        st.success("Account created successfully. Please log in.")

# Dashboards
def citizen_dashboard():
    st.title(f"Welcome, {st.session_state['username']}")
    st.subheader("Citizen Dashboard")
    st.write("Here you can manage your service requests, payments, documents, and feedback.")
    # Add additional components for the Citizen Dashboard

def admin_dashboard():
    st.title(f"Welcome, {st.session_state['username']}")
    st.subheader("Government Administrator Dashboard")
    st.write("Manage services, users, analytics, and system configurations here.")
    # Add additional components for the Administrator Dashboard

def officer_dashboard():
    st.title(f"Welcome, {st.session_state['username']}")
    st.subheader("Service Officer Dashboard")
    st.write("Manage and process service requests, citizen information, and tasks.")
    # Add additional components for the Service Officer Dashboard

# Main Application Logic
def main():
    init_db()
    if "role" not in st.session_state:
        welcome_page()
    else:
        role = st.session_state["role"]
        if role == "Citizen":
            citizen_dashboard()
        elif role == "Service Officer":
            officer_dashboard()
        elif role == "Government Administrator":
            admin_dashboard()

def welcome_page():
    st.title("E-Gov Portal")
    st.image("gov_image.webp", use_column_width=True)
    st.subheader("Simplifying Government Services for You")
    st.write("Welcome to the E-Government Platform, where you can easily access a wide range of government services online.")

    if st.button("Register Now"):
        register()
    if st.button("Login"):
        login()

    st.markdown("### Key Features")
    st.write(" - Apply for Licenses and Permits Online")
    st.write(" - Make Payments and Track Transactions")
    st.write(" - Access Government Forms and Documents")
    st.write(" - Provide Feedback and Suggestions")

if __name__ == "__main__":
    main()
