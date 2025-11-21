import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

db_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(db_string)
connection = engine.connect()

# FULL SCHEMA WITH CASCADING DELETES
create_sql = """
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS job_applications CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS addresses CASCADE;
DROP TABLE IF EXISTS members CASCADE;
DROP TABLE IF EXISTS caregivers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    given_name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20),
    profile_description TEXT,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE caregivers (
    caregiver_user_id INTEGER PRIMARY KEY,
    photo VARCHAR(255),
    gender VARCHAR(10),
    caregiving_type VARCHAR(50),
    hourly_rate DECIMAL(10, 2),
    CONSTRAINT fk_caregiver_user FOREIGN KEY (caregiver_user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE members (
    member_user_id INTEGER PRIMARY KEY,
    house_rules TEXT,
    dependent_description TEXT,
    CONSTRAINT fk_member_user FOREIGN KEY (member_user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE addresses (
    member_user_id INTEGER NOT NULL,
    house_number VARCHAR(20),
    street VARCHAR(100),
    town VARCHAR(50),
    CONSTRAINT fk_address_member FOREIGN KEY (member_user_id) REFERENCES members (member_user_id) ON DELETE CASCADE
);

CREATE TABLE jobs (
    job_id SERIAL PRIMARY KEY,
    member_user_id INTEGER NOT NULL,
    required_caregiving_type VARCHAR(50),
    other_requirements TEXT,
    date_posted DATE DEFAULT CURRENT_DATE,
    CONSTRAINT fk_job_member FOREIGN KEY (member_user_id) REFERENCES members (member_user_id) ON DELETE CASCADE
);

CREATE TABLE job_applications (
    caregiver_user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    date_applied DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (caregiver_user_id, job_id),
    CONSTRAINT fk_app_caregiver FOREIGN KEY (caregiver_user_id) REFERENCES caregivers (caregiver_user_id) ON DELETE CASCADE,
    CONSTRAINT fk_app_job FOREIGN KEY (job_id) REFERENCES jobs (job_id) ON DELETE CASCADE
);

-- THE CRITICAL FIX IS HERE (ON DELETE CASCADE)
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    caregiver_user_id INTEGER NOT NULL,
    member_user_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    work_hours INTEGER,
    status VARCHAR(20) DEFAULT 'Pending',
    CONSTRAINT fk_appt_caregiver FOREIGN KEY (caregiver_user_id) REFERENCES caregivers (caregiver_user_id) ON DELETE CASCADE,
    CONSTRAINT fk_appt_member FOREIGN KEY (member_user_id) REFERENCES members (member_user_id) ON DELETE CASCADE
);
"""

try:
    connection.execute(text(create_sql))
    connection.commit()
    print("Tables rebuilt successfully with CASCADE rules.")
except Exception as e:
    print(f"Error: {e}")

connection.close()