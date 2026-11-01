
# SafarSathi – Tours & Travels

## 1. Project Introduction
SafarSathi is a web-based Tours & Travels booking application developed using Python and Streamlit. It helps users explore tour packages and submit booking requests through a simple interface.

## 2. Project Overview
The application provides a platform where users can register, log in, browse available tour packages, and manage their bookings. An admin dashboard is also available to manage booking requests.

## 3. Key Features
- User Registration and Login
- Tour Package Listing
- Tour Package Details
- Booking Request Submission
- My Bookings Section
- Admin Dashboard
- Booking Status Management
- MySQL Database Integration

## 4. Technologies Used
- Python
- Streamlit
- MySQL
- MySQL Connector
- Python-dotenv

## 5. Project Folder Structure
```text
SafarSathi/
│
├── app.py
├── db.py
├── security.py
├── schema.sql
├── requirements.txt
├── README.md
├── .gitignore
└── images/
```

## 6. Installation Instructions

Clone the repository:

```bash
git clone https://github.com/bob872002/SafarSathi-Tours-and-Travels.git
```

Open the project folder:

```bash
cd SafarSathi-Tours-and-Travels
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## 7. MySQL Database Setup

1. Open MySQL.
2. Create the database using the provided `schema.sql` file.
3. Configure the database connection details in your local environment.
4. Make sure the database server is running.

**Note:** Do not upload your `.env` file or database passwords to GitHub.

## 8. Application Execution

Run the application using:

```bash
streamlit run app.py
```

The application will open in your default web browser.

## 9. Application Workflow

1. User registers an account.
2. User logs into the application.
3. User explores available tour packages.
4. User submits a booking request.
5. User checks booking details in My Bookings.
6. Admin reviews and updates booking status.

## 10. Manual Testing Scope

The application can be tested for:

- User Registration
- User Login
- Duplicate Email Validation
- Tour Package Display
- Booking Request Submission
- My Bookings
- Admin Access and Booking Management
- Form Validation
- Navigation and Usability

## 11. Author Information

**Developed by:** Jitendra Kumar Yadav

**GitHub:** https://github.com/bob872002
