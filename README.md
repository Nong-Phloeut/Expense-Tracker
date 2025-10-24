# Django Expense Management System

## 🧩 Project Setup Steps

### 1. Clone the Repository

git clone https://github.com/yourusername/expense-management.git
cd expense-management

## 2. Create Virtual Environment

python -m venv venv

## 3.Activate Virtual Environment

Windows
venv\Scripts\activate

Mac/Linux
source venv/bin/activate

### 4. Install Dependencie

pip install -r requirements.txt

## 5. Apply Migration

python manage.py makemigrations
python manage.py migrate

## 6. Create Superuser (Optional)

python manage.py createsuperuser

## 7. Run Development Serve

python manage.py runserver

Then open the app in your browser:
http://127.0.0.1:8000/
