-- ===============================
-- test-sample.sql
-- ===============================

DROP TABLE IF EXISTS Salary;
DROP TABLE IF EXISTS JobPosting;
DROP TABLE IF EXISTS Blacklist;
DROP TABLE IF EXISTS Employer;

-- Employer
CREATE TABLE Employer (
  employer_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  blacklist_flag TINYINT(1) DEFAULT 0
);

-- JobPosting
CREATE TABLE JobPosting (
  job_id INT AUTO_INCREMENT PRIMARY KEY,
  employer_id INT,
  title VARCHAR(255),
  location VARCHAR(100),
  term VARCHAR(20),
  FOREIGN KEY (employer_id) REFERENCES Employer(employer_id)
);

-- Salary
CREATE TABLE Salary (
  salary_id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT UNIQUE,
  hourly_rate DECIMAL(6,2),
  hours_per_week INT,
  notes TEXT,
  FOREIGN KEY (job_id) REFERENCES JobPosting(job_id)
);

-- Blacklist
CREATE TABLE Blacklist (
  blacklist_id INT AUTO_INCREMENT PRIMARY KEY,
  employer_id INT,
  reason TEXT,
  date_added DATE,
  FOREIGN KEY (employer_id) REFERENCES Employer(employer_id)
);

-- ===============================
-- Sample Data
-- ===============================
INSERT INTO Employer (name) VALUES
('Google'),
('Shopify'),
('TinyStart'),
('BadCorp');

INSERT INTO JobPosting (employer_id, title, location, term) VALUES
(1, 'SWE Intern', 'Waterloo', 'Winter 2025'),
(2, 'Data Intern', 'Toronto', 'Fall 2025'),
(3, 'Web Intern', 'Kitchener', 'Winter 2025'),
(4, 'Support Intern', 'Waterloo', 'Winter 2025');

INSERT INTO Salary (job_id, hourly_rate, hours_per_week, notes) VALUES
(1, 45.00, 40, 'Good pay'),
(2, 35.00, 40, 'Solid pay'),
(3, 16.00, 40, 'Low pay'),
(4, 12.00, 40, 'Very low pay');

INSERT INTO Blacklist (employer_id, reason, date_added) VALUES
(4, 'Low pay and poor conditions', '2025-01-10');

-- ===============================
UPDATE Employer e
SET e.blacklist_flag = 1
WHERE EXISTS (
  SELECT 1 FROM Blacklist b WHERE b.employer_id = e.employer_id
);

UPDATE Employer e
LEFT JOIN Blacklist b ON b.employer_id = e.employer_id
SET e.blacklist_flag = 0
WHERE b.employer_id IS NULL;

-- ===============================
-- Test Queries
-- ===============================

-- 1. Employers with flag
SELECT employer_id, name, blacklist_flag
FROM Employer
ORDER BY employer_id;

-- 2. Jobs with salary info
SELECT e.name, j.title, s.hourly_rate
FROM Employer e
JOIN JobPosting j ON e.employer_id = j.employer_id
JOIN Salary s ON j.job_id = s.job_id
ORDER BY s.hourly_rate DESC;

-- 3. Companies paying below $18/hour
SELECT e.name, s.hourly_rate
FROM Employer e
JOIN JobPosting j ON e.employer_id = j.employer_id
JOIN Salary s ON j.job_id = s.job_id
WHERE s.hourly_rate < 18
ORDER BY s.hourly_rate;