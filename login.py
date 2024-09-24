import streamlit as st
import sqlite3
import hashlib

def verify_user(username, password):
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?',
                   (username, hashlib.sha256(str.encode(password)).hexdigest()))
    user = cursor.fetchone()
    conn.close()
    return user

st.title('Login')

username = st.text_input('Username')
password = st.text_input('Password', type='password')

if st.button('Login'):
    user = verify_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.role = user[4]  # Fetch the role
        st.success(f'Welcome {user[1]}!')
        st.experimental_rerun()
    else:
        st.error('Invalid login credentials')
