-- =====================================
-- Co-op Salary Explorer Database Schema
-- =====================================

-- Drop tables in correct order (child tables first)
DROP TABLE IF EXISTS Placement;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Blacklist;
DROP TABLE IF EXISTS Salary;
DROP TABLE IF EXISTS JobPosting;
DROP TABLE IF EXISTS Employer;

-- Drop existing procedures and triggers
DROP PROCEDURE IF EXISTS AddToBlacklist;
DROP TRIGGER IF EXISTS UpdateBlacklistFlag;
DROP TRIGGER IF EXISTS auto_flag_low_pay;
DROP TRIGGER IF EXISTS auto_flag_low_pay_2;

-- ------------------------------
-- Employer Table
-- ------------------------------
CREATE TABLE Employer (
    employer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    blacklist_flag BOOLEAN DEFAULT FALSE,
    CHECK (name <> '')
) ENGINE=InnoDB;

-- ------------------------------
-- JobPosting Table
-- ------------------------------
CREATE TABLE JobPosting (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    employer_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(100),
    term VARCHAR(50),
    FOREIGN KEY (employer_id)
        REFERENCES Employer(employer_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (title <> '')
) ENGINE=InnoDB;

-- ------------------------------
-- Salary Table
-- ------------------------------
CREATE TABLE Salary (
    salary_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    hourly_rate DECIMAL(8,2) NOT NULL CHECK (hourly_rate >= 0),
    hours_per_week INT CHECK (hours_per_week BETWEEN 0 AND 80),
    notes TEXT,
    FOREIGN KEY (job_id)
        REFERENCES JobPosting(job_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------
-- Blacklist Table
-- ------------------------------
CREATE TABLE Blacklist (
    blacklist_id INT AUTO_INCREMENT PRIMARY KEY,
    employer_id INT NOT NULL,
    reason TEXT NOT NULL,
    date_added DATE DEFAULT (CURRENT_DATE),
    added_by VARCHAR(100),
    FOREIGN KEY (employer_id)
        REFERENCES Employer(employer_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------
-- Student Table
-- ------------------------------
CREATE TABLE Student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    faculty VARCHAR(100) NOT NULL,
    program VARCHAR(100) NOT NULL,
    year INT,
    CHECK (name <> ''),
    CHECK (faculty <> ''),
    CHECK (program <> '')
) ENGINE=InnoDB;

-- ------------------------------
-- Placement Table
-- ------------------------------
CREATE TABLE Placement (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (student_id)
        REFERENCES Student(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (job_id)
        REFERENCES JobPosting(job_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =====================================
-- Add FULLTEXT Indexes AFTER table creation
-- =====================================
ALTER TABLE Employer ADD FULLTEXT INDEX ft_employer_name (name);
ALTER TABLE JobPosting ADD FULLTEXT INDEX ft_job_title (title);
ALTER TABLE JobPosting ADD FULLTEXT INDEX ft_job_location (location);

-- =====================================
-- Example Stored Procedure
-- =====================================
DELIMITER $$

CREATE PROCEDURE AddToBlacklist(
    IN emp_id INT,
    IN reason_text TEXT,
    IN added_by_user VARCHAR(100)
)
BEGIN
    INSERT INTO Blacklist (employer_id, reason, added_by)
    VALUES (emp_id, reason_text, added_by_user);

    UPDATE Employer
    SET blacklist_flag = TRUE
    WHERE employer_id = emp_id;
END$$

DELIMITER ;

-- =====================================
-- Trigger: Automatically update blacklist_flag
-- =====================================
DELIMITER $$

CREATE TRIGGER UpdateBlacklistFlag
AFTER INSERT ON Blacklist
FOR EACH ROW
BEGIN
    UPDATE Employer
    SET blacklist_flag = TRUE
    WHERE employer_id = NEW.employer_id;
END$$

DELIMITER ;

-- =====================================
-- Trigger: Compute average pay across all jobs of an employer after Salary INSERT; conditionally blacklist employer
-- =====================================
DELIMITER $$

CREATE TRIGGER auto_flag_low_pay AFTER INSERT ON Salary
FOR EACH ROW
BEGIN
DECLARE emp_id INT;
DECLARE avg_rate DECIMAL(6,2);

-- Get employer_id from JobPosting table
SELECT employer_id INTO emp_id
FROM JobPosting
WHERE job_id = NEW.job_id;

-- Compute the employer’s new average rate across all their jobs
SELECT AVG(hourly_rate) INTO avg_rate
FROM Salary s
JOIN JobPosting j ON s.job_id = j.job_id
WHERE j.employer_id = emp_id;

-- If new average rate < $20/hour, flag and add a blacklist entry
IF avg_rate < 20.00 THEN
UPDATE Employer
SET blacklist_flag = TRUE
WHERE employer_id = emp_id;

-- Insert default reason into Blacklist table
INSERT INTO Blacklist (employer_id, reason, date_added, added_by)
VALUES (emp_id, 'Auto-flagged for low average pay', CURDATE(), 'admin@system.com');
END IF;

END$$

DELIMITER ;

-- =====================================
-- Trigger: Compute average pay across all jobs of an employer after Salary UPDATE; conditionally blacklist employer
-- =====================================
DELIMITER $$

CREATE TRIGGER auto_flag_low_pay_update AFTER UPDATE ON Salary
FOR EACH ROW
BEGIN
DECLARE emp_id INT;
DECLARE avg_rate DECIMAL(6,2);

-- Get employer_id from JobPosting table
SELECT employer_id INTO emp_id
FROM JobPosting
WHERE job_id = NEW.job_id;

-- Compute the employer’s new average rate across all their jobs
SELECT AVG(hourly_rate) INTO avg_rate
FROM Salary s
JOIN JobPosting j ON s.job_id = j.job_id
WHERE j.employer_id = emp_id;

-- If new average rate < $20/hour, flag and add a blacklist entry
IF avg_rate < 20.00 THEN
UPDATE Employer
SET blacklist_flag = TRUE
WHERE employer_id = emp_id;

-- Insert default reason into Blacklist table
INSERT INTO Blacklist (employer_id, reason, date_added, added_by)
VALUES (emp_id, 'Auto-flagged for low average pay', CURDATE(), 'admin@system.com');
END IF;

END$$

DELIMITER ;


-- =====================================
-- Sample Data
-- =====================================
INSERT INTO Employer (name) VALUES ('Google'), ('Meta'), ('Amazon'), ('Microsoft'), ('Apple');

INSERT INTO JobPosting (employer_id, title, location, term)
VALUES
    (1, 'Software Engineer Intern', 'Waterloo, ON', 'Winter 2025'),
    (2, 'Data Analyst Co-op', 'Toronto, ON', 'Spring 2025'),
    (3, 'Backend Developer', 'Vancouver, BC', 'Fall 2024'),
    (4, 'Machine Learning Engineer', 'Montreal, QC', 'Winter 2025'),
    (5, 'iOS Developer', 'Toronto, ON', 'Summer 2025');

INSERT INTO Salary (job_id, hourly_rate, hours_per_week)
VALUES
    (1, 38.50, 40),
    (2, 32.00, 37),
    (3, 35.75, 40),
    (4, 42.00, 40),
    (5, 40.25, 38);

INSERT INTO Student (name, faculty, program, year) VALUES 
    ('John Doe', 'Engineering', 'Computer Engineering', 3),
    ('Jane Smith', 'Mathematics', 'Computer Science', 2),
    ('Bob Johnson', 'Engineering', 'Software Engineering', 4);

INSERT INTO Placement (student_id, job_id, start_date, end_date) VALUES
    (1, 1, '2025-01-06', '2025-04-25'),
    (2, 2, '2025-05-05', '2025-08-29'),
    (3, 4, '2025-01-06', '2025-04-25');

-- Example blacklist entry
CALL AddToBlacklist(2, 'Reported unfair interview process', 'AdminUser');