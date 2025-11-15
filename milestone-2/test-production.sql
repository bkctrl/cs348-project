-- ===============================
-- test-production.sql
-- contains only the SQL queries to run on the already loaded large production dataset. (no tables are to be created)
-- uses LIMIT clauses
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
ORDER BY j.job_id
LIMIT 10;

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
ORDER BY avg_hourly_rate DESC, n_placements DESC
LIMIT 10;

-- Feature 4: Average Hourly Salary by Term
SELECT
  j.term,
  ROUND(AVG(s.hourly_rate), 2) AS avg_hourly,
  COUNT(*) AS n_reports
FROM JobPosting j
JOIN Salary s ON s.job_id = j.job_id
GROUP BY j.term
ORDER BY j.term
LIMIT 10;

-- Feature 5: View Blacklisted Employers
SELECT
  e.name AS employer_name,
  b.reason,
  b.date_added
FROM Employer e
JOIN Blacklist b ON e.employer_id = b.employer_id
WHERE e.blacklist_flag = 1
ORDER BY b.date_added DESC, e.name
LIMIT 10;
