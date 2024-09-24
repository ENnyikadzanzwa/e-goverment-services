import streamlit as st
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password, email, role):
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Users (Username, Password, Email, Role) VALUES (?, ?, ?, ?)',
                   (username, hash_password(password), email, role))
    conn.commit()
    conn.close()

st.title('Signup')

# Use a form to group the fields together and prevent early submission
with st.form(key='signup_form'):
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    email = st.text_input('Email')
    role = st.selectbox('Role', ['citizen', 'administrator', 'service officer'])

    # Submit button for the form
    submit_button = st.form_submit_button(label='Signup')

# Only process when the form is submitted
if submit_button:
    # Ensure all fields are filled
    if not username or not password or not email:
        st.error("Please fill out all fields.")
    else:
        create_user(username, password, email, role)
        st.success('User created successfully! Redirecting to login page...')
        
        # Set session state to navigate to the login page
        st.session_state.page = 'login'
        
        # Use a short delay before reloading to ensure the success message is visible
        import time
        time.sleep(2)  # Adjust as necessary
        st.experimental_rerun()  # Force a page reload to apply changes
