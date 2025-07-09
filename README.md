Conference Registration Project Project Description This Django project implements a simple conference registration system. Participants can register by entering their name and email, then fill out additional information (family members count, arrival and departure dates). Admins and superusers access the admin panel to manage participants and see a dashboard summarizing participant data.

Features Participant registration without password (login by name + email).

Admin and superuser login via Django admin interface.

Dashboard for admins showing total participants and detailed participant data.

Participant profile editing.

Clean URL structure with separated apps for main site pages and user management.

Project Structure main app: handles general pages (home, about, conference info).

users app: handles participant registration, login by email and name, and participant profile.

Django admin panel is used for admin/superuser access and management.

Prerequisites Python 3.13+

Django 5.2.4+

Virtual environment (recommended)

SQLite (default DB) or your choice of database

Setup Instructions Clone the repository

git clone cd Create and activate a virtual environment

bash

python -m venv venv

On Windows
venv\Scripts\activate

On Mac/Linux
source venv/bin/activate Install dependencies

bash

pip install -r requirements.txt Configure the secret key

Create a .env file in the project root with the following content:

ini

SECRET_KEY=your-very-secret-key-here Make sure your settings.py reads this key securely, for example:

python Копировать Редактировать import os from dotenv import load_dotenv

load_dotenv() SECRET_KEY = os.getenv('SECRET_KEY') Apply migrations

bash

python manage.py migrate Create superusers / admins

bash

python manage.py createsuperuser

Follow prompts to create admin users
Run the development server

bash

python manage.py runserver Access the application

Open your browser and go to: http://127.0.0.1:8000/ — main site http://127.0.0.1:8000/users/register/ — participant registration/login form http://127.0.0.1:8000/admin/ — admin panel for admins and superusers

Usage notes Participants register or log in by entering name and email, no password required.

Admins and superusers log in through the Django admin interface with username and password.

Admin dashboard is accessible via /admin/dashboard/ (you may add a link or navigate directly).

Participant data includes family members count and arrival/departure dates for demo purposes.

You can extend the dashboard with more stats and visualizations later.

Future Improvements Implement email verification or OAuth login for participants.

Add password recovery options for admins.

Enhance dashboard UI with charts and filters.

Deploy with Docker and configure production-ready settings.
