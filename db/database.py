import sqlite3

def create_tables():
    conn = sqlite3.connect('e_gov.db')  # Connect to the database
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE,
        Password TEXT,
        Email TEXT,
        Role TEXT)''')

    # Create Citizen_Profile table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Citizen_Profile (
        Citizen_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        User_ID INTEGER,
        Name TEXT,
        DOB TEXT,
        Address TEXT,
        Phone_Number TEXT,
        FOREIGN KEY (User_ID) REFERENCES Users(User_ID))''')

    # Create Services table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Services (
        Service_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Service_Name TEXT,
        Service_Description TEXT,
        Category TEXT)''')

    # Create Service_Requests table (with Officer_ID)
    cursor.execute('''CREATE TABLE IF NOT EXISTS Service_Requests (
        Request_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Citizen_ID INTEGER,
        Service_ID INTEGER,
        Officer_ID INTEGER,
        Request_Status TEXT,
        Request_Date TEXT,
        FOREIGN KEY (Citizen_ID) REFERENCES Citizen_Profile(Citizen_ID),
        FOREIGN KEY (Service_ID) REFERENCES Services(Service_ID),
        FOREIGN KEY (Officer_ID) REFERENCES Users(User_ID))''')

    # Create Payments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Payments (
        Payment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Request_ID INTEGER,
        Payment_Method TEXT,
        Payment_Date TEXT,
        Payment_Amount REAL,
        FOREIGN KEY (Request_ID) REFERENCES Service_Requests(Request_ID))''')

    # Create Documents table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Documents (
        Document_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Request_ID INTEGER,
        Document_Type TEXT,
        Document_Content BLOB,
        FOREIGN KEY (Request_ID) REFERENCES Service_Requests(Request_ID))''')

    # Create Feedback table with Request_ID
    cursor.execute('''CREATE TABLE IF NOT EXISTS Feedback (
        Feedback_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Request_ID INTEGER,
        Citizen_ID INTEGER,
        Service_ID INTEGER,
        Feedback_Rating INTEGER,
        Feedback_Comment TEXT,
        FOREIGN KEY (Request_ID) REFERENCES Service_Requests(Request_ID),
        FOREIGN KEY (Citizen_ID) REFERENCES Citizen_Profile(Citizen_ID),
        FOREIGN KEY (Service_ID) REFERENCES Services(Service_ID))''')

    # Create Notifications table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Notifications (
        Notification_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        User_ID INTEGER,
        Message TEXT,
        Date_Sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (User_ID) REFERENCES Users(User_ID))''')

    # Create System_Settings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS System_Settings (
        Setting_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Setting_Name TEXT UNIQUE,
        Value TEXT)''')

    # Insert default password policy into System_Settings if not already present
    cursor.execute('''INSERT OR IGNORE INTO System_Settings (Setting_Name, Value) 
                      VALUES ('Password_Policy', 'Minimum 8 characters, 1 number, 1 special character')''')

    conn.commit()
    conn.close()
