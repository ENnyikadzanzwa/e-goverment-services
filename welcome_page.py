import streamlit as st

def welcome_page():
    st.title('Welcome to the E-Government Portal')
    

    st.header('Simplifying Government Services for You')
    st.write('''Access a variety of government services online:
    - Apply for licenses, permits, and certifications
    - Submit complaints or feedback
    - Track service requests and payments
    - And much more!''')

    st.subheader('Get Started')

    col1, col2 = st.columns(2)

    # Button to navigate to the signup page
    with col1:
        if st.button('Register Now', key='signup'):
            st.session_state.page = 'signup'  # Set session state to indicate signup navigation

    # Button to navigate to the login page
    with col2:
        if st.button('Login', key='login'):
            st.session_state.page = 'login'  # Set session state to indicate login navigation

    st.image('gov_image.webp', use_column_width=True)