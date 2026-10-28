# College Event Management System (CEMS)

A student-friendly DBMS mini project built with Python Flask, MySQL, HTML, CSS and Bootstrap.

## Features
- View events and dashboard totals
- Add college events
- Register students for events
- Prevent duplicate registration for the same event (database UNIQUE constraint)
- View registrations using JOIN queries
- Store and view event results/winners

## Requirements
- Python 3.10+
- MySQL Server and MySQL Workbench (or another MySQL client)
- VS Code or another code editor
- Internet connection for Bootstrap CDN styling

## Step 1 — Create the database
1. Open MySQL Workbench and connect to your local MySQL server.
2. Open `schema.sql`.
3. Run the whole script (lightning icon).
4. Confirm that `college_event_db` and its four tables appear in the Schemas panel.

The script inserts sample students, events, registrations and one sample result. If you run it again, the sample event rows may be duplicated; for a clean reset, drop the database first and rerun the script:
`DROP DATABASE college_event_db;`

## Step 2 — Configure Python
Open a terminal in this project folder and create a virtual environment:

Windows:
```powershell
py -m venv .venv
.venv\\Scripts\\activate
```

Install dependencies:
```powershell
python -m pip install -r requirements.txt
```

## Step 3 — Set your MySQL password
Open `app.py` and replace `YOUR_MYSQL_PASSWORD` with the password for your MySQL `root` account. If your MySQL account has no password, use an empty string: `""`.

For a real deployment, create a separate database user and do not commit credentials to public GitHub.

## Step 4 — Run the app
```powershell
python app.py
```
Open the address printed in the terminal, usually `http://127.0.0.1:5000`.

## Step 5 — Test the GUI
1. View the event cards and dashboard counts.
2. Add an event from the form on the home page.
3. Open an event and register a student.
4. Visit **Registrations** to verify the saved row.
5. Visit **Results** to record a winner and view the result.

## Database design
- `students`: one row per student; email is unique.
- `events`: event details and registration capacity.
- `registrations`: junction table connecting students and events; composite uniqueness prevents a student registering twice for the same event.
- `results`: winners/positions for events.

## Useful SQL queries for viva/demo
```sql
USE college_event_db;

-- 1. List all events
SELECT * FROM events;

-- 2. Count registrations per event
SELECT e.title, COUNT(r.registration_id) AS total_registrations
FROM events e LEFT JOIN registrations r ON e.event_id = r.event_id
GROUP BY e.event_id, e.title;

-- 3. Show participant names with event names (JOIN)
SELECT s.full_name, e.title, r.registration_date
FROM registrations r
JOIN students s ON s.student_id = r.student_id
JOIN events e ON e.event_id = r.event_id;

-- 4. Students registered for CodeSprint
SELECT s.full_name, s.email
FROM students s
JOIN registrations r ON r.student_id = s.student_id
JOIN events e ON e.event_id = r.event_id
WHERE e.title = 'CodeSprint';

-- 5. Events with no registrations
SELECT e.title FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
WHERE r.registration_id IS NULL;

-- 6. Winners and their positions
SELECT e.title, s.full_name, res.position
FROM results res
JOIN events e ON e.event_id = res.event_id
JOIN students s ON s.student_id = res.student_id
ORDER BY e.title, res.position;

-- 7. Count students by department
SELECT department, COUNT(*) AS student_count
FROM students GROUP BY department;

-- 8. Find events above average registration count
SELECT event_title, total_registrations
FROM (
  SELECT e.title AS event_title, COUNT(r.registration_id) AS total_registrations
  FROM events e LEFT JOIN registrations r ON r.event_id=e.event_id
  GROUP BY e.event_id, e.title
) AS event_counts
WHERE total_registrations > (
  SELECT AVG(reg_count) FROM (
    SELECT COUNT(r2.registration_id) AS reg_count
    FROM events e2 LEFT JOIN registrations r2 ON r2.event_id=e2.event_id
    GROUP BY e2.event_id
  ) AS counts_by_event
);
```

## Concepts demonstrated
DDL (`CREATE TABLE`), DML (`INSERT`), `SELECT`, `JOIN`, `GROUP BY`, aggregate functions (`COUNT`, `AVG`), subqueries, primary keys, foreign keys, `UNIQUE` constraints and form validation.
