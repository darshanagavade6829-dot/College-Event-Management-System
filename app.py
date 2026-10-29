
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.security import check_password_hash
import mysql.connector
from mysql.connector import Error



load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_PATH = os.path.join(BASE_DIR, os.getenv("CA_PATH", "isrgrootx1.pem"))



DB_CONFIG = {
    "host": os.getenv("TIDB_HOST"),
    "port": int(os.getenv("TIDB_PORT", "4000")),
    "user": os.getenv("TIDB_USER"),
    "password": os.getenv("TIDB_PASSWORD"),
    "database": os.getenv("TIDB_DB_NAME", "college_event_db"),
    "ssl_ca": CA_PATH,
    "ssl_verify_cert": True,
    "ssl_verify_identity": True,
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT e.*, COUNT(r.registration_id) AS registered_count
        FROM events e
        LEFT JOIN registrations r ON e.event_id = r.event_id
        GROUP BY e.event_id
        ORDER BY e.event_date ASC
    """)
    events = cur.fetchall()
    cur.execute("SELECT COUNT(*) AS total FROM students")
    student_count = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM registrations")
    registration_count = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM events")
    event_count = cur.fetchone()["total"]
    cur.close()
    conn.close()
    return render_template("index.html", events=events, student_count=student_count,
                           registration_count=registration_count, event_count=event_count)

@app.route("/events/add", methods=["POST"])
def add_event():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    event_date = request.form.get("event_date", "")
    venue = request.form.get("venue", "").strip()
    capacity = request.form.get("capacity", "50")
    if not title or not event_date or not venue:
        flash("Please complete the event title, date, and venue.", "error")
        return redirect(url_for("index"))
    try:
        capacity = max(1, int(capacity))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (title, description, event_date, venue, capacity) VALUES (%s,%s,%s,%s,%s)",
            (title, description, event_date, venue, capacity)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Event added successfully.", "success")
    except (ValueError, Error) as exc:
        flash(f"Could not add event: {exc}", "error")
    return redirect(url_for("index"))

@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
    event = cur.fetchone()
    if not event:
        cur.close()
        conn.close()
        flash("Event not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "")
        if not name or not email or not department or not year:
            flash("Please fill in all fields.", "error")
        else:
            try:
                cur.execute("SELECT student_id FROM students WHERE email = %s", (email,))
                student = cur.fetchone()
                if student:
                    student_id = student["student_id"]
                    cur.execute("UPDATE students SET full_name=%s, department=%s, study_year=%s WHERE student_id=%s",
                                (name, department, int(year), student_id))
                else:
                    cur.execute("INSERT INTO students (full_name, email, department, study_year) VALUES (%s,%s,%s,%s)",
                                (name, email, department, int(year)))
                    student_id = cur.lastrowid
                cur.execute("SELECT COUNT(*) AS total FROM registrations WHERE event_id=%s", (event_id,))
                registered = cur.fetchone()["total"]
                if registered >= event["capacity"]:
                    conn.rollback()
                    flash("Sorry, this event has reached its registration capacity.", "error")
                else:
                    cur.execute("INSERT INTO registrations (student_id, event_id) VALUES (%s,%s)", (student_id, event_id))
                    conn.commit()
                    flash("Registration successful!", "success")
                    cur.close()
                    conn.close()
                    return redirect(url_for("index"))
            except Error as exc:
                conn.rollback()
                if getattr(exc, "errno", None) == 1062:
                    flash("This student is already registered for this event.", "error")
                else:
                    flash(f"Registration failed: {exc}", "error")
            except ValueError:
                conn.rollback()
                flash("Please select a valid study year.", "error")

    cur.close()
    conn.close()
    return render_template("register.html", event=event)

@app.route("/registrations")
def registrations():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.registration_id, r.registration_date, s.full_name, s.email,
               s.department, s.study_year, e.title AS event_title, e.event_date
        FROM registrations r
        JOIN students s ON r.student_id = s.student_id
        JOIN events e ON r.event_id = e.event_id
        ORDER BY r.registration_date DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("registrations.html", rows=rows)

@app.route("/results", methods=["GET", "POST"])
def results():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        event_id = request.form.get("event_id")
        student_id = request.form.get("student_id")
        position = request.form.get("position")
        if event_id and student_id and position:
            try:
                cur.execute("INSERT INTO results (event_id, student_id, position) VALUES (%s,%s,%s)",
                            (int(event_id), int(student_id), int(position)))
                conn.commit()
                flash("Result saved.", "success")
            except Error as exc:
                conn.rollback()
                flash(f"Could not save result: {exc}", "error")
    cur.execute("SELECT event_id, title FROM events ORDER BY title")
    events = cur.fetchall()
    cur.execute("SELECT student_id, full_name, email FROM students ORDER BY full_name")
    students = cur.fetchall()
    cur.execute("""
        SELECT e.title AS event_title, s.full_name, r.position
        FROM results r JOIN events e ON r.event_id=e.event_id
        JOIN students s ON r.student_id=s.student_id
        ORDER BY e.title, r.position
    """)
    winners = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("results.html", events=events, students=students, winners=winners)

if __name__ == "__main__":
    app.run(debug=True)
