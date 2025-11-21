from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to Database
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

db_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(db_string)

@app.route('/')
def index():
    return render_template('index.html')

# --- READ: View all Users ---
@app.route('/users')
def users():
    with engine.connect() as conn:
        # Fetch all users ordered by ID
        result = conn.execute(text("SELECT * FROM users ORDER BY user_id"))
        users_list = result.fetchall()
    return render_template('users.html', users=users_list)

# --- CREATE: Add a new User ---
@app.route('/add_user', methods=['POST'])
def add_user():
    email = request.form['email']
    given_name = request.form['given_name']
    surname = request.form['surname']
    city = request.form['city']
    password = request.form['password']
    phone = request.form.get('phone', '') # Optional

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO users (email, given_name, surname, city, password, phone_number) 
            VALUES (:email, :given_name, :surname, :city, :password, :phone)
        """), {
            "email": email, "given_name": given_name, 
            "surname": surname, "city": city, 
            "password": password, "phone": phone
        })
        conn.commit()
    
    return redirect(url_for('users'))

# --- DELETE: Remove a User ---
@app.route('/delete_user/<int:id>')
def delete_user(id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users WHERE user_id = :id"), {"id": id})
        conn.commit()
    return redirect(url_for('users'))

if __name__ == '__main__':
    app.run(debug=True)