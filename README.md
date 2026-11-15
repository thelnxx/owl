# ‼️ Pay Attention
- Please note that the documentation below is solely for describing the project; the project is being developed incrementally and new versions will be released over time...
- To run the project in your local environment, make sure you are using at least the following versions of the required programs and frameworks:
  - **Python**: v3.14.7
  - **Django**: v6.1
  - **Bootstrap**: v5.3

# 🚀 Owl Nightly

> A helpful owl for students.

<!-- BADGES -->
[![Python](https://img.shields.io/badge/Python-3.14.7-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
![SQLite](https://img.shields.io/badge/SQLite-Sqlite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

## 📌 About the Project

This project is a modern web application developed using the Django web framework. Its goal is to provide a dynamically built educational and learning environment for students.

### 📸 Screenshots
| Home Page | Admin Panel |
| :---: | :---: |
| ![Home Page](https://via.placeholder.com/400x220?text=No+image+added+yet) | ![Admin Panel](https://via.placeholder.com/400x220?text=No+image+added+yet) |

---

## ✨ Features

- ⚡ **RESTful API:** Integrated API endpoints built with Django REST Framework.
- 🎨 **User Interface:** Clean and responsive interfaces styled with Bootstrap v5.3.
- 🗄️ **Database Optimization:** Indexing and ORM query optimizations powered by SQLite3.

---

## 🛠️ Technologies Used

- **Backend:** Python 3.14.7, Django 5.3, Django REST Framework
- **Frontend:** HTML5, Bootstrap, JavaScript
- **Database:** SQLite3
- **DevOps & Tools:** Docker, Docker Compose, Git, VSCode

---

## ⚙️ Installation & Setup

### 1. Local Setup

Follow the steps below in order to run the project on your local machine:

#### Prerequisites
- Python 3.14+
- Git
- SQLite

#### Step 1: Clone the repository
```bash
git clone [https://github.com/thelnxx/owl-nightly.git](https://github.com/thelnxx/owl-nightly.git)
cd owl-nightly
```

#### Step 2: Create and activate a virtual environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt / PowerShell)
python -m venv venv
venv\Scripts\activate
```

#### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure environment variables
```bash
cp .env.example .env
```
*(Update the `SECRET_KEY` and database credentials inside the file according to your setup.)*

#### Step 5: Run database migrations
```bash
python manage.py migrate
```

#### Step 6: Create a superuser (Admin)
```bash
python manage.py createsuperuser
```

#### Step 7: Start the development server
```bash
python manage.py runserver
```
You can access the application in your browser at `http://127.0.0.1:8000/`.

---

### 2. Docker Setup (Optional)

If you have Docker and Docker Compose installed on your system, you can spin up all services with a single command:

```bash
docker-compose up --build -d
```
Once the containers are running, apply the database migrations:
```bash
docker-compose exec web python manage.py migrate
```

## 🧪 Running Tests

To run the project's unit tests:

```bash
py manage.py test
```

Or if you are using `pytest`:
```bash
pytest
```

---

## 🪲 Running the Project in Debug Mode

To view additions, removals, updates, and fixes made to the project in real time, replace the `DEBUG = False` line inside your `settings.py` file with the following code block so you can immediately see changes and track development:
```python
DEBUG = True
```
then run the following command:
```bash
py manage.py runserver
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
