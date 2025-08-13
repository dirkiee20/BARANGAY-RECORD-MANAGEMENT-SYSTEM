# Barangay Record Management System (BRMS)

A comprehensive, web-based system designed to streamline and digitize the management of resident records, blotter cases, and clearance requests for a local barangay.

## Features

-   **Secure User Authentication**: Role-based login system for administrators and staff with robust password validation.
-   **Dashboard**: An at-a-glance overview of key statistics like population, households, active blotter cases, and recent activities.
-   **Resident Management**: Create, view, update, and manage detailed resident profiles, including personal information and profile pictures.
-   **Household Management**: Group residents into households.
-   **Blotter System**: Record and track community disputes and incidents.
-   **Clearance & Certificate Issuance**: Manage requests for Barangay Clearances, Certificates of Indigency, and other documents.
-   **Search Functionality**: Quickly find residents or records.
-   **Responsive Design**: A modern, dark-themed interface that works on both desktop and mobile devices.

## Tech Stack

-   **Backend**: Python, Flask
-   **Database**: PostgreSQL
-   **ORM**: Flask-SQLAlchemy
-   **Migrations**: Flask-Migrate
-   **Authentication**: Flask-Login
-   **Forms**: Flask-WTF
-   **Frontend**: HTML, CSS, JavaScript (no framework)

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

-   Python 3.8+
-   PostgreSQL

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd record_management_system
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment.

**On Windows:**
```bash
python -m venv env
.\env\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 4. Install Dependencies

Install all the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 5. Configure the Database

1.  Make sure your PostgreSQL server is running.
2.  Create a new database for the project (e.g., `brms_db`).
3.  Create a database user with privileges for the new database.

### 6. Set Up Environment Variables

Create a `.env` file in the root directory of the project by copying the example file:
```bash
copy .env.example .env  # On Windows
cp .env.example .env    # On macOS/Linux
```

Now, edit the `.env` file with your database credentials and a secret key.

### 7. Run Database Migrations

Initialize the database schema using Flask-Migrate:
```bash
flask db upgrade
```
This will create all the necessary tables in your database.

### 8. Run the Application

You can now start the Flask development server:
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

## Usage

1.  Navigate to `http://127.0.0.1:5000/register` in your browser.
2.  Create an administrator account by selecting the "Admin" role.
3.  Log in with your new credentials at `http://127.0.0.1:5000/`.
4.  You can now access the dashboard and manage barangay records.