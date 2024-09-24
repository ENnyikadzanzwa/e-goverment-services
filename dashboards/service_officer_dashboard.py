import streamlit as st
import sqlite3
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_connection():
    conn = sqlite3.connect('e_gov.db')
    return conn
# Function to get assigned service requests for the officer
def get_assigned_service_requests(officer_id):
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Service_Requests WHERE Officer_ID=?', (officer_id,))
    requests = cursor.fetchall()
    conn.close()
    return requests



# Function to get all service requests (not limited to officer_id)
def get_all_service_requests():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Service_Requests')
    requests = cursor.fetchall()
    conn.close()
    return requests



def add_feedback_date_column():
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()
    
    # Add Feedback_Date column to Feedback table if it doesn't exist
    cursor.execute('''ALTER TABLE Feedback ADD COLUMN Feedback_Date TEXT DEFAULT CURRENT_TIMESTAMP''')
    
    conn.commit()
    conn.close()



# Function to update service request status
def update_request_status(request_id, new_status):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Service_Requests SET Request_Status=? WHERE Request_ID=?', (new_status, request_id))
    conn.commit()
    conn.close()

def get_citizen_profiles():
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()
    
    # Case-insensitive check for the "Citizen" role
    cursor.execute('SELECT * FROM Users WHERE LOWER(Role) = "citizen"')
    
    citizens = cursor.fetchall()
    conn.close()
    return citizens


# Function to get workload and feedback for a service officer
def get_workload_with_feedback(officer_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sr.Request_ID, s.Service_Name, f.Feedback_Comment, f.Feedback_Rating
        FROM Service_Requests sr
        JOIN Services s ON sr.Service_ID = s.Service_ID
        JOIN Feedback f ON sr.Citizen_ID = f.Citizen_ID AND sr.Service_ID = f.Service_ID
        WHERE sr.Officer_ID = ?
    ''', (officer_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks
def get_workload(officer_id):
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()

    # Query to fetch workload (service requests) for the officer
    cursor.execute('''SELECT sr.Request_ID, s.Service_Name, sr.Request_Status, f.Feedback_Comment 
                      FROM Service_Requests sr
                      JOIN Services s ON sr.Service_ID = s.Service_ID
                      LEFT JOIN Feedback f ON sr.Request_ID = f.Request_ID
                      WHERE sr.Officer_ID = ?''', (officer_id,))
    
    workload = cursor.fetchall()
    conn.close()
    return workload


def get_all_feedbacks():
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()

    # Fetch feedback details along with the service name and feedback date
    cursor.execute('''SELECT f.Feedback_Comment, f.Feedback_Rating, s.Service_Name 
                      FROM Feedback f
                      JOIN Services s ON f.Service_ID = s.Service_ID''')
    
    feedbacks = cursor.fetchall()
    conn.close()
    return feedbacks


# Function to display workload management with feedback analytics
def workload_management(officer_id):
    st.subheader("Workload Management")
    
    # Fetch workload data
    workload = get_workload_with_feedback(officer_id)
    
    if workload:
        # Create a DataFrame from workload data
        workload_df = pd.DataFrame(workload, columns=["Request ID", "Service", "Feedback Comment", "Feedback Rating"])
        
        # Display the raw data
        st.write("Tasks with Citizen Feedback:")
        st.dataframe(workload_df)
        
        # Plot the feedback rating distribution
        if "Feedback Rating" in workload_df.columns and not workload_df["Feedback Rating"].isna().all():
            st.subheader("Feedback Rating Distribution")
            fig = px.histogram(workload_df, x="Feedback Rating", nbins=10, title="Citizen Feedback Ratings")
            st.plotly_chart(fig)
        
        # Average feedback rating per service
        avg_feedback = workload_df.groupby('Service')['Feedback Rating'].mean().reset_index()
        st.subheader("Average Feedback Rating per Service")
        st.dataframe(avg_feedback)
        
        # Plot average feedback rating per service
        fig_avg = px.bar(avg_feedback, x="Service", y="Feedback Rating", title="Average Feedback Rating by Service")
        st.plotly_chart(fig_avg)
    else:
        st.write("No tasks with citizen feedback found.")


# Function to get citizen info by citizen ID
def get_citizen_info(citizen_id):
    conn = sqlite3.connect('e_gov.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Citizen_Profile WHERE Citizen_ID=?', (citizen_id,))
    citizen_info = cursor.fetchone()
    conn.close()
    return citizen_info

def service_officer_dashboard(officer_id):
    st.title("Service Officer Dashboard")

    # Tab layout for dashboard sections
    tabs = st.tabs(["Service Requests", "Citizen Information", "Communication", "Analytics and Feedback"])

    # 1. Service Requests Tab
    with tabs[0]:
        st.subheader("All Service Requests")
        
        # Get all service requests from database
        service_requests = get_all_service_requests()
        
        if service_requests:
            for req in service_requests:
                st.write(f"Request ID: {req[0]} | Citizen ID: {req[1]} | Status: {req[3]} | Date: {req[4]}")
                
                # Create a dropdown for status update
                new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed"], key=f"status_{req[0]}")
                
                # Button to update status for each request
                if st.button(f"Update Status for Request {req[0]}", key=f"update_{req[0]}"):
                    update_request_status(req[0], new_status)
                    st.success(f"Request {req[0]} status updated to {new_status}")
        else:
            st.write("No service requests found.")

    # 2. Workload Management Tab
    with tabs[1]:
        st.header("Analytics & Reporting")
        
        st.subheader("Generate Custom Reports")
        report_type = st.selectbox("Report Type", ["Service Usage", "Payment Trends", "Citizen Feedback"])
        
        if st.button("Generate Report"):
            st.write(f"Generating {report_type} report...")

            conn = create_connection()
            cursor = conn.cursor()
            
            if report_type == "Service Usage":
                st.subheader("Service Usage Report")
                
                # Fetch service usage statistics
                cursor.execute('''SELECT s.Service_Name, COUNT(sr.Request_ID) AS Request_Count
                                FROM Services s
                                LEFT JOIN Service_Requests sr ON s.Service_ID = sr.Service_ID
                                GROUP BY s.Service_ID''')
                usage_stats = cursor.fetchall()
                conn.close()
                
                # Display the result in a table
                st.write("**Service Usage Table:**")
                if usage_stats:
                    usage_df = pd.DataFrame(usage_stats, columns=["Service Name", "Request Count"])
                    st.dataframe(usage_df)

                    # Plot service usage statistics using Plotly
                    fig = px.bar(usage_df, x='Service Name', y='Request Count', title="Service Usage Statistics")
                    st.plotly_chart(fig)
                else:
                    st.write("No service usage data available.")
            
            elif report_type == "Payment Trends":
                st.subheader("Payment Trends Report")
                
                # Fetch payment trends statistics
                cursor.execute('''SELECT p.Payment_Date, SUM(p.Payment_Amount) AS Total_Payments
                                FROM Payments p
                                GROUP BY p.Payment_Date''')
                payment_stats = cursor.fetchall()
                conn.close()

                # Display the result in a table
                st.write("**Payment Trends Table:**")
                if payment_stats:
                    payment_df = pd.DataFrame(payment_stats, columns=["Payment Date", "Total Payments"])
                    st.dataframe(payment_df)

                    # Plot payment trends using Plotly
                    fig = px.line(payment_df, x='Payment Date', y='Total Payments', title="Payment Trends Over Time")
                    st.plotly_chart(fig)
                else:
                    st.write("No payment trends data available.")
            
            elif report_type == "Citizen Feedback":
                st.subheader("Citizen Feedback Report")
                
                # Fetch citizen feedback statistics
                cursor.execute('''SELECT f.Feedback_Comment, f.Feedback_Rating, s.Service_Name
                                FROM Feedback f
                                JOIN Services s ON f.Service_ID = s.Service_ID''')
                feedback_stats = cursor.fetchall()
                conn.close()

                # Display the result in a table
                st.write("**Citizen Feedback Table:**")
                if feedback_stats:
                    feedback_df = pd.DataFrame(feedback_stats, columns=["Feedback Comment", "Feedback Rating", "Service Name"])
                    st.dataframe(feedback_df)

                    # Plot feedback ratings using Plotly
                    fig = px.histogram(feedback_df, x='Feedback Rating', title="Citizen Feedback Ratings")
                    st.plotly_chart(fig)
                else:
                    st.write("No citizen feedback data available.")

    # 4. Communication Tab
    # System Configuration Tab
    with tabs[2]:
        st.header("System Configuration")
        
        # Section for sending security notifications to citizens
        st.subheader("Send Security Notifications to Citizens")
        
        # Fetch citizens from the database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT User_ID, Username, Email FROM Users WHERE Role='citizen'")
        citizens = cursor.fetchall()
        conn.close()
        
        if citizens:
            # Multi-select for choosing which citizens to notify
            selected_citizens = st.multiselect("Select Citizens to Notify", [f"{citizen[1]} (Email: {citizen[2]})" for citizen in citizens])
            
            # Input box for writing the notification message
            notification_message = st.text_area("Write Notification Message", placeholder="Enter your security update message here...")
            
            if st.button("Send Notification"):
                # Extract the User_IDs of selected citizens
                citizen_ids = [citizen[0] for citizen in citizens if f"{citizen[1]} (Email: {citizen[2]})" in selected_citizens]
                
                if notification_message and citizen_ids:
                    conn = create_connection()
                    cursor = conn.cursor()
                    
                    # Store notifications in a table (you'll need a Notifications table for this)
                    for citizen_id in citizen_ids:
                        cursor.execute("INSERT INTO Notifications (User_ID, Message) VALUES (?, ?)", (citizen_id, notification_message))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("Notification sent to the selected citizens!")
                else:
                    st.error("Please select citizens and write a notification message.")
        else:
            st.write("No citizens available to notify.")
        
        # Section for updating security settings
        st.subheader("Security Settings")
        st.write("Update security measures for citizens to secure their accounts.")
        
        password_policy = st.text_input("Update Password Policy", placeholder="E.g., Minimum 8 characters, one number, one special character")
        
        if st.button("Update Security Policy"):
            # Assuming there's a table where system settings are stored
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE System_Settings SET Value=? WHERE Setting_Name='Password_Policy'", (password_policy,))
            conn.commit()
            conn.close()
            
            st.success("Security policy updated successfully!")

    with tabs[3]:
        st.subheader("Citizen Feedback Analytics")
        
        feedbacks = get_all_feedbacks()
        if feedbacks:
            feedback_df = pd.DataFrame(feedbacks, columns=["Feedback Comment", "Feedback Rating", "Service Name"])
            
            # Display feedback data
            st.write("**All Citizen Feedbacks:**")
            st.dataframe(feedback_df)
            
            # Visualize Feedback Ratings as a Pie Chart
            rating_count = feedback_df['Feedback Rating'].value_counts().reset_index()
            rating_count.columns = ['Rating', 'Count']
            fig = px.pie(rating_count, names='Rating', values='Count', title="Distribution of Feedback Ratings")
            st.plotly_chart(fig)
            
            
            
        else:
            st.write("No feedback data available.")
