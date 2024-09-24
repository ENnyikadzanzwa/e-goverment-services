# Initialize session state to track the current page
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Initialize session state to track the current username
if 'username' not in st.session_state:
    st.session_state.username = None

# Main page function
def main_page():
    # Your main page content here
    pass

# Login page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.username = username
            st.session_state.page = 'main'
        else:
            st.error("Invalid username or password.")

# Signup page
def signup_page():
    st.title("Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    role = st.selectbox("Select Role", ["Citizen", "Service Officer", "Government Administrator"])
    if st.button("Signup"):
        if create_user(username, password, email, role):
            st.success("Account created successfully!")
            st.session_state.page = 'login'
        else:
            st.error("Username or email already exists!")

# Initialize session state to track the current page
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Initialize session state to track the current username
if 'username' not in st.session_state:
    st.session_state.username = None

# Main page function
def main_page():
    # Your main page content here
    pass

# Login page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.username = username
            st.session_state.page = 'main'
        else:
            st.error("Invalid username or password.")

# Signup page
def signup_page():
    st.title("Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    role = st.selectbox("Select Role", ["Citizen", "Service Officer", "Government Administrator"])
    if st.button("Signup"):
        if create_user(username, password, email, role):
            st.success("Account created successfully!")
            st.session_state.page = 'login'
        else:
            st.error("Username or email already exists!")

# Check the current page and display the corresponding content
if st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'signup':
    signup_page()
elif st.session_state.page == 'main':
    main_page()