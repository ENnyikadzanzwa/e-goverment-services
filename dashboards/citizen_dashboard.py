import streamlit as st
import sqlite3
from datetime import datetime

# Connect to the database
def connect_db():
    return sqlite3.connect('e_gov.db')

# Retrieve service requests for a citizen
def get_service_requests(citizen_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT sr.Request_ID, sr.Request_Status, sr.Request_Date, s.Service_Name
                      FROM Service_Requests sr
                      JOIN Services s ON sr.Service_ID = s.Service_ID
                      WHERE sr.Citizen_ID=?''', (citizen_id,))
    requests = cursor.fetchall()
    conn.close()
    return requests

# Retrieve payment history for a citizen
def get_payment_history(citizen_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT p.Payment_ID, p.Payment_Amount, p.Payment_Date, s.Service_Name
                      FROM Payments p
                      JOIN Service_Requests sr ON p.Request_ID = sr.Request_ID
                      JOIN Services s ON sr.Service_ID = s.Service_ID
                      WHERE sr.Citizen_ID=?''', (citizen_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments

# Retrieve documents for a citizen
def get_documents(citizen_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT d.Document_ID, d.Document_Type, sr.Request_ID
                      FROM Documents d
                      JOIN Service_Requests sr ON d.Request_ID = sr.Request_ID
                      WHERE sr.Citizen_ID=?''', (citizen_id,))
    documents = cursor.fetchall()
    conn.close()
    return documents

# Retrieve feedback for a citizen
def submit_feedback(citizen_id, service_id, rating, comment):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Feedback (Citizen_ID, Service_ID, Feedback_Rating, Feedback_Comment)
                      VALUES (?, ?, ?, ?)''', (citizen_id, service_id, rating, comment))
    conn.commit()
    conn.close()

# Retrieve notifications for a citizen
def get_notifications(citizen_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT Message, Date_Sent FROM Notifications
                      WHERE User_ID=? ORDER BY Date_Sent DESC''', (citizen_id,))
    notifications = cursor.fetchall()
    conn.close()
    return notifications

# Insert a new document into the database
def upload_document(request_id, doc_type, doc_content):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Documents (Request_ID, Document_Type, Document_Content) VALUES (?, ?, ?)',
                   (request_id, doc_type, doc_content))
    conn.commit()
    conn.close()

# Insert a new payment into the database
def make_payment(request_id, payment_amount, payment_method):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Payments (Request_ID, Payment_Amount, Payment_Method, Payment_Date) VALUES (?, ?, ?, ?)',
                   (request_id, payment_amount, payment_method, datetime.now().strftime('%Y-%m-%d')))  # Use the current date
    conn.commit()
    conn.close()

# Main function to display the citizen dashboard
def citizen_dashboard():
    st.title('Citizen Dashboard')

    # Ensure that user_id is present in session state
    if 'user_id' not in st.session_state:
        st.error("User ID not found. Please log in again.")
        return

    citizen_id = st.session_state.user_id

    # Create the tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Service Requests', 'Payment History', 'Document Repository', 'Feedback & Support', 'Notifications'])

    # Tab 1: Service Requests
    with tab1:
        st.subheader('Your Service Requests')
        service_requests = get_service_requests(citizen_id)
        if service_requests:
            for req in service_requests:
                st.write(f"Request ID: {req[0]} | Service: {req[3]} | Status: {req[1]} | Date: {req[2]}")
                
                # Option to upload documents for each request
                st.subheader(f"Upload Document for Request ID: {req[0]}")
                uploaded_file = st.file_uploader(f"Upload Document for Request {req[0]}")
                if uploaded_file is not None:
                    doc_type = st.text_input(f"Document Type for Request {req[0]}")
                    if st.button(f"Upload Document for Request {req[0]}"):
                        upload_document(req[0], doc_type, uploaded_file.read())
                        st.success(f"Document uploaded for Request {req[0]}.")
        else:
            st.write("No service requests found.")

        # Option to submit a new request
        st.subheader('Submit New Request')

        # Fetch available services from the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT Service_ID, Service_Name FROM Services')
        services = cursor.fetchall()
        conn.close()

        if services:
            service_names = [s[1] for s in services]
            selected_service_name = st.selectbox("Select Service", service_names)

            # Find corresponding service ID directly
            service_id = next(s[0] for s in services if s[1] == selected_service_name)

            if st.button('Submit Request'):
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO Service_Requests (Citizen_ID, Service_ID, Request_Status, Request_Date) VALUES (?, ?, ?, ?)',
                               (citizen_id, service_id, 'Pending', datetime.now().strftime('%Y-%m-%d')))
                conn.commit()
                conn.close()
                st.success("Service request submitted.")
        else:
            st.error("No services available.")

    # Tab 2: Payment History
    with tab2:
        st.subheader('Your Payment History')
        payments = get_payment_history(citizen_id)
        if payments:
            for payment in payments:
                st.write(f"Payment ID: {payment[0]} | Amount: {payment[1]} | Date: {payment[2]} | Service: {payment[3]}")
        else:
            st.write("No payments found.")
        
        # Option to make a new payment
        st.subheader('Make a New Payment')

        # Retrieve the service requests to select a request ID
        service_requests = get_service_requests(citizen_id)
        if service_requests:
            request_ids = [req[0] for req in service_requests]
            request_id = st.selectbox("Select Service Request", request_ids)
            payment_amount = st.number_input("Payment Amount", min_value=0.0)
            payment_method = st.selectbox("Payment Method", ['Credit Card', 'Bank Transfer', 'Mobile Money'])
            if st.button('Make Payment'):
                make_payment(request_id, payment_amount, payment_method)
                st.success("Payment successful!")
        else:
            st.write("No service requests available to make a payment.")

    # Tab 3: Document Repository
    with tab3:
        st.subheader('Your Document Repository')
        documents = get_documents(citizen_id)
        if documents:
            for doc in documents:
                st.write(f"Document ID: {doc[0]} | Type: {doc[1]} | Related Request ID: {doc[2]}")
        else:
            st.write("No documents found.")
        
        # Option to upload a new document for a specific request
        uploaded_file = st.file_uploader("Upload Document")
        if uploaded_file is not None:
            doc_type = st.text_input("Document Type")
            request_ids = [req[0] for req in get_service_requests(citizen_id)]
            if request_ids:
                request_id = st.selectbox("Related Request ID", request_ids)
                if st.button("Upload Document"):
                    upload_document(request_id, doc_type, uploaded_file.read())
                    st.success("Document uploaded successfully!")
            else:
                st.write("No service requests available to associate the document with.")

    # Tab 4: Feedback and Support
    with tab4:
        st.subheader('Submit Feedback or Complaint')

        # Fetch available services for feedback
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT Service_ID, Service_Name FROM Services')
        services = cursor.fetchall()
        conn.close()

        if services:
            service_names = [s[1] for s in services]
            selected_service_name = st.selectbox("Service", service_names)

            # Find corresponding service ID directly
            service_id = next(s[0] for s in services if s[1] == selected_service_name)

            rating = st.slider('Rating', 1, 5)
            comment = st.text_area('Comment')
            if st.button('Submit Feedback'):
                submit_feedback(citizen_id, service_id, rating, comment)
                st.success("Feedback submitted.")
        else:
            st.error("No services available for feedback.")

        # Support contact information
        st.subheader('Contact Support')
        st.write("Email: support@egovplatform.com")
        st.write("Phone: +123 456 7890")

    # Tab 5: Notifications
    with tab5:
        st.subheader('Notifications')
        notifications = get_notifications(citizen_id)
        if notifications:
            for notification in notifications:
                st.write(f"Date: {notification[1]} | Message: {notification[0]}")
        else:
            st.write("No new notifications.")
