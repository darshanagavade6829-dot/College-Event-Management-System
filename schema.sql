CREATE DATABASE IF NOT EXISTS college_event_db;
USE college_event_db;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    department VARCHAR(60) NOT NULL,
    study_year TINYINT NOT NULL,
    CHECK (study_year BETWEEN 1 AND 4)
);

CREATE TABLE IF NOT EXISTS events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    venue VARCHAR(120) NOT NULL,
    capacity INT NOT NULL DEFAULT 50,
    CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    event_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_registration_student FOREIGN KEY (student_id)
        REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_registration_event FOREIGN KEY (event_id)
        REFERENCES events(event_id) ON DELETE CASCADE,
    CONSTRAINT uq_student_event UNIQUE (student_id, event_id)
);

CREATE TABLE IF NOT EXISTS results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    student_id INT NOT NULL,
    position TINYINT NOT NULL,
    CONSTRAINT fk_result_event FOREIGN KEY (event_id)
        REFERENCES events(event_id) ON DELETE CASCADE,
    CONSTRAINT fk_result_student FOREIGN KEY (student_id)
        REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT uq_event_position UNIQUE (event_id, position),
    CONSTRAINT uq_event_student UNIQUE (event_id, student_id),
    CHECK (position > 0)
);

INSERT INTO students (full_name, email, department, study_year) VALUES
('Aarav Patil', 'aarav.patil@example.com', 'Computer Engineering', 2),
('Sneha Deshmukh', 'sneha.d@example.com', 'Information Technology', 2),
('Rohan Jadhav', 'rohan.j@example.com', 'Artificial Intelligence', 3)
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO events (title, description, event_date, venue, capacity) VALUES
('CodeSprint', 'A coding competition for college students.', '2027-01-15', 'Computer Lab 1', 80),
('TechQuiz', 'A team-based technology quiz.', '2027-01-20', 'Seminar Hall', 60),
('Project Expo', 'Showcase student projects and prototypes.', '2027-02-05', 'Main Auditorium', 100);

INSERT INTO registrations (student_id, event_id)
SELECT s.student_id, e.event_id FROM students s JOIN events e ON e.title='CodeSprint'
WHERE s.email='aarav.patil@example.com'
ON DUPLICATE KEY UPDATE registration_id=registration_id;

INSERT INTO registrations (student_id, event_id)
SELECT s.student_id, e.event_id FROM students s JOIN events e ON e.title='TechQuiz'
WHERE s.email='sneha.d@example.com'
ON DUPLICATE KEY UPDATE registration_id=registration_id;

INSERT INTO results (event_id, student_id, position)
SELECT e.event_id, s.student_id, 1 FROM events e JOIN students s
ON e.title='CodeSprint' AND s.email='aarav.patil@example.com'
ON DUPLICATE KEY UPDATE position=VALUES(position);
