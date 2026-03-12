# PokeVault API - COMP3011 Coursework 1

**Student Name:** Yichen Huang
**Student ID:** 201656189

Hosted on an external web server
You can test the fully deployed production API here
Live URL: `https://Er1CShelby.pythonanywhere.com/api/`

## Project Overview
This project is a RESTful Web API designed for the *COMP3011: Web Services and Web Data* module. It serves as a backend system for a Pokémon Trading Card Game (TCG) collection manager.

The API allows users to:
* Manage a personal collection of cards (Create, Read, Update, Delete).
* View reference data for Pokémon cards (fetched from external sources).
* Filter cards by name or rarity.
* Track collection quantity and purchase price.

I chose **Django** and **Django REST Framework** for this project because they provide a robust, standard architecture for handling relational databases and object serialization, which aligns with the module's teaching on Model-View-Controller patterns.

**[Click here to view the official API Documentation (PDF)](./API_Documentation.pdf)**

## Tech Stack
* **Language:** Python 3.10+
* **Framework:** Django 5.1.7, Django REST Framework 3.15.2
* **Database:** SQLite
* **External Integration:** `requests` library used to fetch real card data from the TCGdex API.

## Installation & Setup Instructions

Follow these steps to set up the project and run it on your local machine.

### Clone the Repository
Open your terminal and clone the repository from GitHub:
```bash
git clone https://github.com/Er1cSHelby/COMP3011_Coursework1.git

cd COMP3011_Coursework1
```

### 1. Install requirements.txt
```bash
pip install -r requirements.txt
```

### 2. Apply Database Migrations
Before running the server, ensure the database is initialized with the correct schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Fetch Initial Data
Run the data ingestion script to fetch real Pokémon card data from the TCGdex API:
```bash
python fetch_data.py
```

### 4. Run the Local Development Server
```bash
python manage.py runserver
```
The API will now be accessible locally at http://127.0.0.1:8000/api/

- /api/health/: Basic health check to verify the API is running.
- /api/sets/: Retrieve a list of all Pokémon TCG Expansion Sets.
- /api/cards/: Retrieve all Pokémon Cards.
- /api/collection/: Manage your personal card collection

### Admin Dashboard
To manage the global database
Create a superuser account in your terminal:
```bash
python manage.py createsuperuser
```
Navigate to http://127.0.0.1:8000/admin/ and log in with your new credentials


## Project Structure

This project follows a standard Django and Django REST Framework (DRF) architecture. Below is a breakdown of the core directories and files:

### Root Directory
* **`manage.py`**: Django's built-in command-line utility. It is used to run administrative tasks such as starting the local development server, making database migrations.
* **`db.sqlite3`**: The default local SQLite database file/
* **`fetch_data.py`**: A Python script built for this coursework. It connects to the external TCGdex API, gets real-time Pokémon card data (including pricing and rarity), and write to the local `db.sqlite3` database.

### `pokevault/` (Project Configuration Folder)
* **`settings.py`**: Contains all the global configurations for the project, including database connections, registered apps (like `api` and `rest_framework`), security keys, and static file settings.
* **`urls.py`**: The master routing file. It acts as the main entry point for all web requests and routes them to the appropriate application URLs.
* **`wsgi.py`**: Configuration files used for deploying the project to a production web server.

### `api/` (Main Application Folder)
* **`models.py`**: Defines the database schema. It contains the Python classes (`Card`, `ExpansionSet`, `CollectionItem`) that Django translates into SQL database tables.
* **`serializers.py`**: Handles the data transformation. It converts complex database models into native Python datatypes that can be easily rendered into standard JSON formats for the web API.
* **`views.py`**: It handles incoming HTTP requests (GET, POST, etc.), queries the database using the models, passes the data to the serializers, and returns the final HTTP response to the client.
* **`urls.py`**: Handles the application-specific URL routing, mapping specific API endpoints (like `/api/cards/`) to their corresponding functions in `views.py`.
* **`admin.py`**: Configuration file to register models with the built-in Django Admin interface, allowing for easy visual management of the database records.
* **`migrations/`**: A directory containing auto-generated Python scripts that keep track of changes made to `models.py` and apply those structural changes to the database.