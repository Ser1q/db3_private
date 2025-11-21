from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# 1. Load variables from .env file
load_dotenv()

# 2. Get variables
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 3. Construct the connection string securely
# format: postgresql://user:password@host:port/dbname
db_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# 2. DEFINE SQL INSERT STATEMENTS
# We use a transaction block to ensure all data goes in together
insert_sql = """
-- CLEAR EXISTING DATA (Optional, prevents duplicates if run multiple times)
TRUNCATE TABLE appointments, job_applications, jobs, addresses, members, caregivers, users CASCADE;

-- ---------------------------
-- 1. INSERT USERS (20 Users)
-- IDs 1-10 will be Caregivers, 11-20 will be Members
-- ---------------------------
INSERT INTO users (user_id, email, given_name, surname, city, phone_number, profile_description, password) VALUES
(1, 'alice@mail.com', 'Alice', 'Smith', 'Astana', '87011111111', 'Experienced nurse', 'pass1'),
(2, 'bob@mail.com', 'Bob', 'Brown', 'Almaty', '87011111112', 'Loves kids', 'pass2'),
(3, 'charlie@mail.com', 'Charlie', 'Davis', 'Astana', '87011111113', 'Patient and kind', 'pass3'),
(4, 'diana@mail.com', 'Diana', 'Evans', 'Shymkent', '87011111114', 'Energetic student', 'pass4'),
(5, 'evan@mail.com', 'Evan', 'Foster', 'Astana', '87011111115', 'Professional care', 'pass5'),
(6, 'fiona@mail.com', 'Fiona', 'Green', 'Almaty', '87011111116', 'Certified babysitter', 'pass6'),
(7, 'george@mail.com', 'George', 'Harris', 'Astana', '87011111117', 'Good with pets too', 'pass7'),
(8, 'hannah@mail.com', 'Hannah', 'White', 'Astana', '87011111118', 'Special needs exp', 'pass8'),
(9, 'ivan@mail.com', 'Ivan', 'Black', 'Almaty', '87011111119', 'Part-time helper', 'pass9'),
(10, 'julia@mail.com', 'Julia', 'Clarke', 'Astana', '87011111120', 'Music tutor and sitter', 'pass10'),

-- Members (IDs 11-20)
(11, 'kevin@mail.com', 'Kevin', 'King', 'Astana', '87771112222', 'Busy father', 'pass11'),
(12, 'laura@mail.com', 'Laura', 'Lee', 'Almaty', '87771113333', 'Need help weekends', 'pass12'),
(13, 'mike@mail.com', 'Mike', 'Miller', 'Astana', '87771114444', 'Looking for elderly care', 'pass13'),
(14, 'nina@mail.com', 'Nina', 'Nelson', 'Shymkent', '87771115555', 'Single mom', 'pass14'),
(15, 'oscar@mail.com', 'Oscar', 'Orton', 'Astana', '87771116666', 'Need urgent help', 'pass15'),
(16, 'paul@mail.com', 'Paul', 'Parker', 'Almaty', '87771117777', 'Frequent traveler', 'pass16'),
(17, 'quinn@mail.com', 'Quinn', 'Quick', 'Astana', '87771118888', 'Three kids', 'pass17'),
(18, 'rachel@mail.com', 'Rachel', 'Red', 'Astana', '87771119999', 'Live near park', 'pass18'),
(19, 'amina@mail.com', 'Amina', 'Aminova', 'Astana', '87770001111', 'Requires regular help', 'pass19'),
(20, 'arman@mail.com', 'Arman', 'Armanov', 'Almaty', '87770002222', 'Looking for professional', 'pass20');


-- ---------------------------
-- 2. INSERT CAREGIVERS (10 rows)
-- Note: Hourly rates mix <10 and >10 for the commission update logic
-- ---------------------------
INSERT INTO caregivers (caregiver_user_id, photo, gender, caregiving_type, hourly_rate) VALUES
(1, 'photo1.jpg', 'F', 'Babysitter', 15.00),
(2, 'photo2.jpg', 'M', 'Elderly Care', 8.00),   -- Rate < 10
(3, 'photo3.jpg', 'M', 'Babysitter', 12.00),
(4, 'photo4.jpg', 'F', 'Playmate for children', 9.00), -- Rate < 10
(5, 'photo5.jpg', 'M', 'Elderly Care', 20.00),
(6, 'photo6.jpg', 'F', 'Babysitter', 11.50),
(7, 'photo7.jpg', 'M', 'Playmate for children', 10.00),
(8, 'photo8.jpg', 'F', 'Elderly Care', 18.00),
(9, 'photo9.jpg', 'M', 'Babysitter', 14.00),
(10, 'photo10.jpg', 'F', 'Playmate for children', 13.00);


-- ---------------------------
-- 3. INSERT MEMBERS (10 rows)
-- ---------------------------
INSERT INTO members (member_user_id, house_rules, dependent_description) VALUES
(11, 'No pets.', 'Elderly father with mobility issues'), -- Fits Query 5.4 (Astana, Elderly, No pets)
(12, 'No smoking', 'Two energetic twins'),
(13, 'Shoes off', 'Grandmother needs company'),
(14, 'Vegetarian food only', '5 year old girl'),
(15, 'Quiet after 9pm', 'Newborn baby'),
(16, 'Be on time', '10 year old boy'),
(17, 'Clean up toys', 'Toddler'),
(18, 'No loud music', 'Sick relative'),
(19, 'Hygiene is priority', 'Daughter needs tutoring'), -- Amina Aminova
(20, 'Safety first', 'Son likes painting');             -- Arman Armanov


-- ---------------------------
-- 4. INSERT ADDRESSES
-- Note: Creating "Kabanbay Batyr" addresses for the DELETE requirement
-- ---------------------------
INSERT INTO addresses (member_user_id, house_number, street, town) VALUES
(11, '10A', 'Mangilik El', 'Astana'),
(12, '5B', 'Abay', 'Almaty'),
(13, '12', 'Turan', 'Astana'),
(14, '77', 'Tauke Khan', 'Shymkent'),
(15, '3', 'Saryarka', 'Astana'),
(16, '99', 'Dostyk', 'Almaty'),
(17, '44', 'Kunaev', 'Astana'),
(18, '101', 'Kabanbay Batyr', 'Astana'), -- TARGET FOR DELETE
(19, '102', 'Kabanbay Batyr', 'Astana'), -- TARGET FOR DELETE (Amina is here too)
(20, '55', 'Gogol', 'Almaty');


-- ---------------------------
-- 5. INSERT JOBS
-- Note: Including 'soft-spoken' for Query 5.2
-- Note: Amina (19) posts jobs for Delete 4.1
-- ---------------------------
INSERT INTO jobs (job_id, member_user_id, required_caregiving_type, other_requirements, date_posted) VALUES
(1, 11, 'Elderly Care', 'Must be strong and patient', '2025-10-01'),
(2, 12, 'Babysitter', 'English speaking preferred', '2025-10-02'),
(3, 13, 'Elderly Care', 'Must be soft-spoken and kind', '2025-10-03'), -- TARGET FOR QUERY 5.2
(4, 14, 'Babysitter', 'Weekend availability', '2025-10-04'),
(5, 19, 'Babysitter', 'Math tutoring required', '2025-10-05'), -- Posted by Amina
(6, 19, 'Playmate for children', 'Artistic skills', '2025-10-06'), -- Posted by Amina
(7, 20, 'Babysitter', 'Driver license needed', '2025-10-07'),
(8, 15, 'Babysitter', 'Night shift', '2025-10-08'),
(9, 16, 'Playmate for children', 'Sports oriented', '2025-10-09'),
(10, 11, 'Elderly Care', 'Cooking skills', '2025-10-10');


-- ---------------------------
-- 6. INSERT JOB APPLICATIONS
-- ---------------------------
INSERT INTO job_applications (caregiver_user_id, job_id, date_applied) VALUES
(1, 2, '2025-10-03'),
(2, 1, '2025-10-02'),
(3, 3, '2025-10-04'),
(4, 6, '2025-10-07'),
(5, 1, '2025-10-02'),
(6, 5, '2025-10-06'),
(1, 4, '2025-10-05'),
(9, 7, '2025-10-08'),
(10, 9, '2025-10-10'),
(8, 10, '2025-10-11');


-- ---------------------------
-- 7. INSERT APPOINTMENTS
-- Note: Status 'Accepted' required for calculations
-- ---------------------------
INSERT INTO appointments (caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status) VALUES
(1, 12, '2025-11-01', '09:00:00', 4, 'Accepted'),
(2, 11, '2025-11-02', '14:00:00', 3, 'Accepted'),
(3, 13, '2025-11-03', '10:00:00', 5, 'Pending'),
(4, 19, '2025-11-04', '12:00:00', 2, 'Accepted'), -- Amina's appointment
(5, 11, '2025-11-05', '08:00:00', 6, 'Declined'),
(6, 12, '2025-11-06', '18:00:00', 3, 'Accepted'),
(8, 15, '2025-11-07', '20:00:00', 8, 'Accepted'),
(9, 20, '2025-11-08', '15:00:00', 4, 'Pending'),
(10, 16, '2025-11-09', '11:00:00', 2, 'Accepted'),
(1, 14, '2025-11-10', '09:00:00', 5, 'Accepted');
"""


try:
    engine = create_engine(db_string)
    connection = engine.connect()
    print(f"Successfully connected to {DB_NAME} at {HOST}!")
except Exception as e:
    print(f"Connection failed: {e}")

    
# 3. EXECUTE
try:
    connection.execute(text(insert_sql))
    connection.commit()
    print("All data inserted successfully!")
except Exception as e:
    print(f"Error inserting data: {e}")
    # Rollback in case of error to avoid partial states
    connection.rollback()

connection.close()