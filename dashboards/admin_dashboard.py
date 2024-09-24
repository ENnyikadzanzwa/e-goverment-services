import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import plotly.express as px

def create_connection():
    try:
        conn = sqlite3.connect('e_gov.db')
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def admin_dashboard():
    # Tab layout
    tabs = st.tabs(["Service Management", "User Management", "Analytics & Reporting", "System Configuration"])

    # Service Management Tab
    with tabs[0]:
        st.header("Service Management")

        try:
            # Fetch all services from the database
            conn = create_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Services")
            services = cursor.fetchall()
            conn.close()

            st.subheader("List of Services")
            for service in services:
                st.write(f"Service ID: {service[0]} | Name: {service[1]} | Description: {service[2]} | Category: {service[3]}")

            st.subheader("Add New Service")
            new_service_name = st.text_input("Service Name")
            new_service_description = st.text_area("Service Description")
            new_service_category = st.text_input("Service Category")

            if st.button("Add Service"):
                conn = create_connection()
                if conn is None:
                    return
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Services (Service_Name, Service_Description, Category) VALUES (?, ?, ?)",
                                   (new_service_name, new_service_description, new_service_category))
                    conn.commit()
                    st.success("Service added successfully!")
                except sqlite3.Error as e:
                    st.error(f"Error adding service: {e}")
                finally:
                    conn.close()
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # User Management Tab
    with tabs[1]:
        st.header("User Management")

        try:
            # Fetch all users from the database
            conn = create_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users")
            users = cursor.fetchall()
            conn.close()

            st.subheader("List of Users")
            for user in users:
                st.write(f"User ID: {user[0]} | Username: {user[1]} | Role: {user[4]}")

            st.subheader("Add/Edit User")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["Select Role", "citizen", "service officer", "administrator"])

            if st.button("Add/Edit User"):
                conn = create_connection()
                if conn is None:
                    return
                try:
                    cursor = conn.cursor()
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute("INSERT INTO Users (Username, Password, Email, Role) VALUES (?, ?, ?, ?)", 
                                   (username, hashed_password, email, role))
                    conn.commit()
                    st.success("User added/edited successfully!")
                except sqlite3.Error as e:
                    st.error(f"Error adding/editing user: {e}")
                finally:
                    conn.close()
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Analytics & Reporting Tab
    with tabs[2]:
        st.header("Analytics & Reporting")

        st.subheader("Generate Custom Reports")
        report_type = st.selectbox("Report Type", ["Service Usage", "Payment Trends", "Citizen Feedback"])

        if st.button("Generate Report"):
            st.write(f"Generating {report_type} report...")

            conn = create_connection()
            if conn is None:
                return
            cursor = conn.cursor()

            try:
                if report_type == "Service Usage":
                    st.subheader("Service Usage Report")

                    cursor.execute('''SELECT s.Service_Name, COUNT(sr.Request_ID) AS Request_Count
                                    FROM Services s
                                    LEFT JOIN Service_Requests sr ON s.Service_ID = sr.Service_ID
                                    GROUP BY s.Service_ID''')
                    usage_stats = cursor.fetchall()
                    conn.close()

                    st.write("**Service Usage Table:**")
                    if usage_stats:
                        usage_df = pd.DataFrame(usage_stats, columns=["Service Name", "Request Count"])
                        st.dataframe(usage_df)

                        fig = px.bar(usage_df, x='Service Name', y='Request Count', title="Service Usage Statistics")
                        st.plotly_chart(fig)
                    else:
                        st.write("No service usage data available.")

                elif report_type == "Payment Trends":
                    st.subheader("Payment Trends Report")

                    cursor.execute('''SELECT p.Payment_Date, SUM(p.Payment_Amount) AS Total_Payments
                                    FROM Payments p
                                    GROUP BY p.Payment_Date''')
                    payment_stats = cursor.fetchall()
                    conn.close()

                    st.write("**Payment Trends Table:**")
                    if payment_stats:
                        payment_df = pd.DataFrame(payment_stats, columns=["Payment Date", "Total Payments"])
                        st.dataframe(payment_df)

                        fig = px.line(payment_df, x='Payment Date', y='Total Payments', title="Payment Trends Over Time")
                        st.plotly_chart(fig)
                    else:
                        st.write("No payment trends data available.")

                elif report_type == "Citizen Feedback":
                    st.subheader("Citizen Feedback Report")

                    cursor.execute('''SELECT f.Feedback_Comment, f.Feedback_Rating, s.Service_Name
                                    FROM Feedback f
                                    JOIN Services s ON f.Service_ID = s.Service_ID''')
                    feedback_stats = cursor.fetchall()
                    conn.close()

                    st.write("**Citizen Feedback Table:**")
                    if feedback_stats:
                        feedback_df = pd.DataFrame(feedback_stats, columns=["Feedback Comment", "Feedback Rating", "Service Name"])
                        st.dataframe(feedback_df)

                        fig = px.histogram(feedback_df, x='Feedback Rating', title="Citizen Feedback Ratings")
                        st.plotly_chart(fig)
                    else:
                        st.write("No citizen feedback data available.")
            except sqlite3.Error as e:
                st.error(f"Error generating report: {e}")

    # System Configuration Tab
    with tabs[3]:
        st.header("System Configuration")

        # Section for sending security notifications to citizens
        st.subheader("Send Security Notifications to Citizens")

        try:
            conn = create_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT User_ID, Username, Email FROM Users WHERE Role='citizen'")
            citizens = cursor.fetchall()
            conn.close()

            if citizens:
                selected_citizens = st.multiselect("Select Citizens to Notify", [f"{citizen[1]} (Email: {citizen[2]})" for citizen in citizens])
                notification_message = st.text_area("Write Notification Message", placeholder="Enter your security update message here...")

                if st.button("Send Notification"):
                    citizen_ids = [citizen[0] for citizen in citizens if f"{citizen[1]} (Email: {citizen[2]})" in selected_citizens]

                    if notification_message and citizen_ids:
                        conn = create_connection()
                        if conn is None:
                            return
                        try:
                            cursor = conn.cursor()
                            for citizen_id in citizen_ids:
                                cursor.execute("INSERT INTO Notifications (User_ID, Message) VALUES (?, ?)", (citizen_id, notification_message))
                            conn.commit()
                            st.success("Notification sent to the selected citizens!")
                        except sqlite3.Error as e:
                            st.error(f"Error sending notification: {e}")
                        finally:
                            conn.close()
                    else:
                        st.error("Please select citizens and write a notification message.")
            else:
                st.write("No citizens available to notify.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

        # Section for updating security settings
        st.subheader("Security Settings")
        st.write("Update security measures for citizens to secure their accounts.")

        password_policy = st.text_input("Update Password Policy", placeholder="E.g., Minimum 8 characters, one number, one special character")

        if st.button("Update Security Policy"):
            try:
                conn = create_connection()
                if conn is None:
                    return
                cursor = conn.cursor()
                cursor.execute("UPDATE System_Settings SET Value=? WHERE Setting_Name='Password_Policy'", (password_policy,))
                conn.commit()
                st.success("Security policy updated successfully!")
            except sqlite3.Error as e:
                st.error(f"Error updating security policy: {e}")
            finally:
                conn.close()

        st.write("Configure integrations with other systems.")
