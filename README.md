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


password super user : 123

// new featur 

add filter in Audit log and export 

✅ **Notes:**

- Always start **worker first**, then **beat**, then **Django server**.  
    ## celery -A config worker -l info
    ## celery -A config beat -l info
- Each command should run in its **own terminal window**.  
- For testing tasks manually, you can use the Django shell.  

---

I can also rewrite it in a **super simple 3-step version** if you want it **short and easy for new devs**. Do you want me to do that?

**1️⃣ Open Django shell**

From your project root:

python manage.py shell


You should see the Python prompt:

>>> 

2️⃣ Import your Celery task
from app.tasks import check_recurring_expenses

3️⃣ Trigger the task with the test flag
check_recurring_expenses.delay(force_send=True)