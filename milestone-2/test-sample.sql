-- ===============================
-- test-sample.sql
-- ===============================

DROP TABLE IF EXISTS Placement;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Salary;
DROP TABLE IF EXISTS JobPosting;
DROP TABLE IF EXISTS Blacklist;
DROP TABLE IF EXISTS Employer;

-- Employer
CREATE TABLE Employer (
  employer_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  blacklist_flag TINYINT(1) NOT NULL DEFAULT 0
);

-- Blacklist
CREATE TABLE Blacklist (
  blacklist_id INT AUTO_INCREMENT PRIMARY KEY,
  employer_id INT NOT NULL,
  reason TEXT NOT NULL,
  date_added DATE NOT NULL,
  added_by VARCHAR(100),
  FOREIGN KEY (employer_id) REFERENCES Employer(employer_id)
);

-- JobPosting
CREATE TABLE JobPosting (
  job_id INT AUTO_INCREMENT PRIMARY KEY,
  employer_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  location VARCHAR(100) NOT NULL,
  term VARCHAR(20) NOT NULL,
  FOREIGN KEY (employer_id) REFERENCES Employer(employer_id)
);

-- Salary
CREATE TABLE Salary (
  salary_id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT NOT NULL UNIQUE,
  hourly_rate DECIMAL(6,2) NOT NULL,
  hours_per_week INT,
  notes TEXT,
  FOREIGN KEY (job_id) REFERENCES JobPosting(job_id)
);

-- Student
CREATE TABLE Student (
  student_id INT PRIMARY KEY,
  faculty VARCHAR(50) NOT NULL,
  program VARCHAR(100) NOT NULL
);

-- Placement
CREATE TABLE Placement (
  student_id INT NOT NULL,
  job_id INT NOT NULL,
  PRIMARY KEY (student_id, job_id),
  FOREIGN KEY (student_id) REFERENCES Student(student_id),
  FOREIGN KEY (job_id) REFERENCES JobPosting(job_id)
);

-- ===============================
-- Sample Data
-- ===============================

-- Employers
INSERT INTO Employer (employer_id, name, blacklist_flag) VALUES
  (1, 'Google', 0),
  (2, 'Microsoft', 0),
  (3, 'TinyStart', 0),
  (4, 'Risky Startup', 1),
  (5, 'Scam Co', 1);

-- Blacklist entries
INSERT INTO Blacklist (employer_id, reason, date_added, added_by) VALUES
  (4, 'Repeatedly failed to pay students', '2025-01-15', 'admin'),
  (5, 'Toxic work environment reported', '2025-02-01', 'admin'),
  (5, 'Rescinded offers last minute', '2025-02-10', 'admin');

-- Job postings
INSERT INTO JobPosting (job_id, employer_id, title, location, term) VALUES
  (1, 1, 'Software Engineer Intern', 'Waterloo, ON', 'Winter 2025'),
  (2, 2, 'Software Engineer Intern', 'Toronto, ON', 'Winter 2025'),
  (3, 3, 'Web Developer Intern', 'Kitchener, ON','Winter 2025'),
  (4, 4, 'Support Intern', 'Waterloo, ON', 'Fall 2025'),
  (5, 5, 'Data Analyst Co-op', 'Toronto, ON', 'Fall 2025'),
  (6, 1, 'Data Analyst Co-op', 'Toronto, ON', 'Fall 2025');

-- Salaries
INSERT INTO Salary (job_id, hourly_rate, hours_per_week, notes) VALUES
  (1, 40.00, 40, 'SWE Google'),
  (2, 50.00, 40, 'SWE Microsoft'),
  (3, 16.00, 40, 'Low pay'),
  (4, 14.00, 40, 'Very low pay'),
  (5, 18.00, 40, 'Below average'),
  (6, 35.00, 40, 'DA Google');

-- Students
INSERT INTO Student (student_id, faculty, program) VALUES
  (101, 'Engineering', 'Computer Science'),
  (102, 'Engineering', 'Computer Science'),
  (103, 'Math', 'Statistics'),
  (104, 'Math', 'Computer Science');

-- Placements
INSERT INTO Placement (student_id, job_id) VALUES
  (101, 1), -- Eng/CS @ Google SWE (40)
  (102, 2), -- Eng/CS @ Microsoft SWE (50)
  (103, 6), -- Math/Stats @ Google DA (35)
  (104, 3); -- Math/CS @ TinyStart Web (16)

-- ===============================
-- Test Queries
-- ===============================

-- Feature 1: Keyword-Based Job Search (q = 'Software')
SELECT
  j.title,
  e.name AS employer,
  j.location,
  j.term,
  s.hourly_rate
FROM JobPosting j
JOIN Employer e ON j.employer_id = e.employer_id
JOIN Salary s ON j.job_id = s.job_id
WHERE j.title LIKE '%Software%'
   OR e.name LIKE '%Software%'
   OR j.location LIKE '%Software%'
ORDER BY j.job_id;

-- Feature 2: Top-Paying Companies by Given Role ('Software Engineer Intern')
SELECT
  e.name AS company,
  ROUND(AVG(s.hourly_rate), 2) AS avg_hourly,
  COUNT(*) AS n_reports
FROM Employer e
JOIN JobPosting j ON j.employer_id = e.employer_id
JOIN Salary s ON s.job_id = j.job_id
WHERE j.title = 'Software Engineer Intern'
GROUP BY e.name
ORDER BY avg_hourly DESC
LIMIT 20;

-- Feature 3: Average Salary by Faculty / Program
SELECT
  s.faculty,
  s.program,
  ROUND(AVG(sa.hourly_rate), 2) AS avg_hourly_rate,
  COUNT(*) AS n_placements
FROM Placement p
JOIN Student s ON p.student_id = s.student_id
JOIN Salary sa ON p.job_id = sa.job_id
JOIN JobPosting j ON p.job_id = j.job_id
WHERE s.faculty = 'Engineering'
  AND s.program LIKE '%Computer Science%'
  AND j.term = 'Winter 2025'
GROUP BY s.faculty, s.program
ORDER BY avg_hourly_rate DESC, n_placements DESC;

-- Feature 4: Average Hourly Salary by Term
SELECT
  j.term,
  ROUND(AVG(s.hourly_rate), 2) AS avg_hourly,
  COUNT(*) AS n_reports
FROM JobPosting j
JOIN Salary s ON s.job_id = j.job_id
GROUP BY j.term
ORDER BY j.term;

-- Feature 5: View Blacklisted Employers
SELECT
  e.name AS employer_name,
  b.reason,
  b.date_added
FROM Employer e
JOIN Blacklist b ON e.employer_id = b.employer_id
WHERE e.blacklist_flag = 1
ORDER BY b.date_added DESC, e.name;
