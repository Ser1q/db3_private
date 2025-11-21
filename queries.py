import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. CONFIGURATION
load_dotenv()
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

db_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(db_string)
connection = engine.connect()

def run_query(title, sql, is_select=True):
    print(f"\n--- {title} ---")
    try:
        result = connection.execute(text(sql))
        if is_select:
            # Fetch headers and rows for clean printing
            headers = result.keys()
            rows = result.fetchall()
            if not rows:
                print("(No results found)")
            else:
                # Simple formatting
                print(f"{headers}") 
                for row in rows:
                    print(row)
        else:
            connection.commit() # Commit changes for Updates/Deletes
            print("Operation executed successfully.")
    except Exception as e:
        print(f"ERROR: {e}")
        connection.rollback()

# ==========================================
# 3. UPDATE STATEMENTS [cite: 84-86]
# ==========================================

# 3.1 Update Arman Armanov's phone number
sql_3_1 = """
UPDATE users 
SET phone_number = '+77773414141' 
WHERE given_name = 'Arman' AND surname = 'Armanov';
"""
run_query("3.1 Update Arman's Phone", sql_3_1, is_select=False)

# 3.2 Update Hourly Rate (Commission)
# Logic: If rate < 10, add 0.3. If rate >= 10, increase by 10%.
sql_3_2 = """
UPDATE caregivers
SET hourly_rate = CASE
    WHEN hourly_rate < 10 THEN hourly_rate + 0.3
    ELSE hourly_rate * 1.10
END;
"""
run_query("3.2 Apply Commission to Hourly Rates", sql_3_2, is_select=False)


# ==========================================
# 4. DELETE STATEMENTS [cite: 87-89]
# ==========================================

# 4.1 Delete jobs posted by Amina Aminova
sql_4_1 = """
DELETE FROM jobs 
WHERE member_user_id = (
    SELECT user_id FROM users WHERE given_name = 'Amina' AND surname = 'Aminova'
);
"""
run_query("4.1 Delete Amina's Jobs", sql_4_1, is_select=False)

# 4.2 Delete members living on Kabanbay Batyr street
sql_4_2 = """
DELETE FROM members 
WHERE member_user_id IN (
    SELECT member_user_id FROM addresses WHERE street = 'Kabanbay Batyr'
);
"""
run_query("4.2 Delete Members on Kabanbay Batyr", sql_4_2, is_select=False)


# ==========================================
# 5. SIMPLE QUERIES [cite: 90-94]
# ==========================================

# 5.1 Caregiver and member names for accepted appointments
sql_5_1 = """
SELECT 
    u_care.given_name AS caregiver_name, 
    u_mem.given_name AS member_name
FROM appointments a
JOIN users u_care ON a.caregiver_user_id = u_care.user_id
JOIN users u_mem ON a.member_user_id = u_mem.user_id
WHERE a.status = 'Accepted';
"""
run_query("5.1 Names in Accepted Appointments", sql_5_1)

# 5.2 Job IDs containing 'soft-spoken' in other_requirements
sql_5_2 = """
SELECT job_id, other_requirements 
FROM jobs 
WHERE other_requirements LIKE '%soft-spoken%';
"""
run_query("5.2 Jobs requiring 'soft-spoken'", sql_5_2)

# 5.3 Work hours of all babysitter positions (appointments)
sql_5_3 = """
SELECT a.appointment_id, a.work_hours
FROM appointments a
JOIN caregivers c ON a.caregiver_user_id = c.caregiver_user_id
WHERE c.caregiving_type = 'Babysitter';
"""
run_query("5.3 Work Hours for Babysitters", sql_5_3)

# 5.4 Members looking for Elderly Care in Astana with 'No pets' rule
# We check if they have posted a job for 'Elderly Care' OR their description implies it.
# Usually, "looking for" implies posted jobs.
sql_5_4 = """
SELECT DISTINCT u.given_name, u.surname, u.city, m.house_rules
FROM members m
JOIN users u ON m.member_user_id = u.user_id
JOIN jobs j ON m.member_user_id = j.member_user_id
WHERE u.city = 'Astana'
  AND m.house_rules LIKE '%No pets%'
  AND j.required_caregiving_type = 'Elderly Care';
"""
run_query("5.4 Members (Astana, Elderly Care, No Pets)", sql_5_4)


# ==========================================
# 6. COMPLEX QUERIES [cite: 95-99]
# ==========================================

# 6.1 Count applicants for each job posted by a member
sql_6_1 = """
SELECT j.job_id, COUNT(ja.caregiver_user_id) as applicant_count
FROM jobs j
LEFT JOIN job_applications ja ON j.job_id = ja.job_id
GROUP BY j.job_id
ORDER BY j.job_id;
"""
run_query("6.1 Applicant Count per Job", sql_6_1)

# 6.2 Total hours spent by caregivers for all accepted appointments
sql_6_2 = """
SELECT SUM(work_hours) as total_hours_accepted
FROM appointments
WHERE status = 'Accepted';
"""
run_query("6.2 Total Hours (Accepted)", sql_6_2)

# 6.3 Average pay of caregivers based on accepted appointments
# Interpreted as: Average hourly rate of caregivers who have accepted appointments
sql_6_3 = """
SELECT AVG(c.hourly_rate) as average_caregiver_pay
FROM caregivers c
JOIN appointments a ON c.caregiver_user_id = a.caregiver_user_id
WHERE a.status = 'Accepted';
"""
run_query("6.3 Avg Pay in Accepted Appointments", sql_6_3)

# 6.4 Caregivers who earn above average (based on accepted appointments)
sql_6_4 = """
SELECT u.given_name, c.hourly_rate
FROM caregivers c
JOIN users u ON c.caregiver_user_id = u.user_id
JOIN appointments a ON c.caregiver_user_id = a.caregiver_user_id
WHERE a.status = 'Accepted'
GROUP BY u.given_name, c.hourly_rate
HAVING c.hourly_rate > (
    SELECT AVG(c2.hourly_rate)
    FROM caregivers c2
    JOIN appointments a2 ON c2.caregiver_user_id = a2.caregiver_user_id
    WHERE a2.status = 'Accepted'
);
"""
run_query("6.4 Caregivers earning > Avg", sql_6_4)


# ==========================================
# 7. DERIVED ATTRIBUTE [cite: 100-101]
# ==========================================

# Calculate total cost (Rate * Hours) for all accepted appointments
sql_7 = """
SELECT SUM(c.hourly_rate * a.work_hours) as total_cost_appointments
FROM appointments a
JOIN caregivers c ON a.caregiver_user_id = c.caregiver_user_id
WHERE a.status = 'Accepted';
"""
run_query("7. Total Cost of Accepted Appointments", sql_7)


# ==========================================
# 8. VIEW OPERATION [cite: 102-103]
# ==========================================

# Create View
sql_8_create = """
CREATE OR REPLACE VIEW view_job_applications AS
SELECT 
    j.job_id, 
    u_mem.given_name as employer,
    u_app.given_name as applicant_name,
    ja.date_applied
FROM job_applications ja
JOIN jobs j ON ja.job_id = j.job_id
JOIN users u_mem ON j.member_user_id = u_mem.user_id
JOIN users u_app ON ja.caregiver_user_id = u_app.user_id;
"""
run_query("8. Creating View", sql_8_create, is_select=False)

# Select from View to demonstrate it works
run_query("8. Selecting from View", "SELECT * FROM view_job_applications;")

connection.close()