import streamlit as st
from welcome_page import *
from db.database import create_tables  # Import the function to create tables
import sqlite3
import bcrypt
import dashboards 
import pandas as pd
import numpy as np
import requests
import openai
from openai import OpenAI
from PIL import Image
from dashboards.citizen_dashboard import citizen_dashboard
from dashboards.service_officer_dashboard import service_officer_dashboard
from dashboards.admin_dashboard import admin_dashboard
import requests
import json
import re  # Import regex for email validation
import bcrypt 
import pandas as pd
import numpy as np


# Set page configuration
st.set_page_config(page_title="E-Government Portal", layout="wide")

# Initialize database and create tables
create_tables()

def create_connection():
    conn = sqlite3.connect('e_gov.db')
    return conn

# Function to validate email
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# Function to validate password
def is_valid_password(password):
    return (len(password) >= 8 and
            any(char.isdigit() for char in password) and
            any(char.isalpha() for char in password) and
            any(not char.isalnum() for char in password))

# Function to create an account
def create_account(username, password, email, role):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)', 
                       (username.lower(), hashed_password, email, role))  # Store username in lower case
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Function to log in and return the user role
def login(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, password, role FROM users WHERE username = ?', (username.lower(),))  # Match username in lower case
    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[1]):
        return True, result[0], result[2]
    return False, None, None

# Initialize session state to track the current page
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'username' not in st.session_state:
    st.session_state.username = None

# Main page function
def main_page():
    st.write("Welcome to your e-gvt platform")
    
    if "role" not in st.session_state:
        st.session_state.page = 'login'  # Redirect to login page
    else:
        role = st.session_state["role"]
        if role == "citizen":
            citizen_dashboard()
        elif role == "service officer":
            officer_id = st.session_state['user_id']
            service_officer_dashboard(officer_id)
        elif role == "administrator":
            admin_dashboard()

    if st.button("Logout"):
        st.session_state.page = 'login'  # Redirect to login page
        st.session_state.username = None  # Clear the username
        st.session_state.role = None  # Clear the role

# Login page
if st.session_state.page == 'login':
    st.title("Welcome to Your E-Government Dashboard")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        success, user_id, role = login(login_username, login_password)
        if success:
            st.session_state.username = login_username
            st.session_state.user_id = user_id
            st.session_state.role = role
            st.success("Login successful!")
            st.session_state.page = 'main'  # Redirect to main page
        else:
            st.error("Invalid username or password.")
    
    if st.button("Don't have an account? Sign up here!"):
        st.session_state.page = 'signup'

# Signup page
elif st.session_state.page == 'signup':
    st.title("Create Account")
    create_username = st.text_input("Username", key="create_username")
    create_password = st.text_input("Password", type="password", key="create_password")
    create_email = st.text_input("Email", key="create_email")
    create_role = st.selectbox("Role", ["Select Role", "citizen", "administrator", "service officer"], key="create_gender")
    
    if st.button("Create Account"):
        if create_role == "Select Role":
            st.error("Please select a role.")
        elif not is_valid_email(create_email):
            st.error("Invalid email address.")
        elif not is_valid_password(create_password):
            st.error("Password must be at least 8 characters long, contain letters, numbers, and at least one special character.")
        else:
            if create_account(create_username, create_password, create_email, create_role):
                st.success("Account created successfully!")
                st.session_state.page = 'login'  # Redirect to login after successful signup
            else:
                st.error("Username or email already exists!")
    
    if st.button("Already have an account? Log in here!"):
        st.session_state.page = 'login'

# Main page
elif st.session_state.page == 'main':
    main_page()

elif st.session_state.page == 'welcome':
    welcome_page()