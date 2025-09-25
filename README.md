<h1 align="center">UWaterloo Reddit-Powered Company Insights</h1>

<p align="center">
  Crowd-sourced insights on <b>pay ranges</b>, <b>benefits</b>, <b>interview experience</b>, and <b>blacklist flags</b> for companies recruiting UW students — mined from r/uwaterloo & related subreddits.
</p>

---

## Project Overview

This project is a **database-driven web application** designed for **University of Waterloo co-op students**.  
It provides insights into salaries, benefits, and company practices to help students make more informed choices about where to apply.

- **Users:** Waterloo students exploring salaries  
- **Admins:** Our team (responsible for maintenance, backup, blacklist handling)  
- **Dataset:** Reddit-sourced co-op salary reports, transformed into relational format with synthetic values filling gaps  

**Key Features:**
- Query salaries by faculty, role, or location  
- Identify top-paying companies  
- Show salary trends across terms  
- Flag companies with blacklist entries  
- Provide both table and chart-based outputs  

---

## Platform & Tech Stack

- **Database:** MySQL (local setup for collaboration)  
- **Backend:** Python (Flask), PHP, Java  
- **Frontend:** HTML, CSS, JavaScript (React optional)  
- **Tools/Libraries:** pandas, matplotlib  

---

## Getting Started

### 1. Prerequisites

- Install [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) (8.0+)  
- (Optional) Install Python 3.9+ with `pandas` and `mysql-connector` for programmatic loading

### 2. Create the Database

```sql
CREATE DATABASE coop_salary_explorer;
USE coop_salary_explorer;
```

### 3. Schema Setup
```sql
-- Employer table
CREATE TABLE Employer (
    employer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    blacklist_flag BOOLEAN DEFAULT FALSE
);

-- Job postings
CREATE TABLE JobPosting (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    employer_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(100),
    term VARCHAR(20),
    FOREIGN KEY (employer_id) REFERENCES Employer(employer_id)
);

-- Salaries
CREATE TABLE Salary (
    salary_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    hourly_rate DECIMAL(6,2) CHECK (hourly_rate >= 0),
    hours_per_week INT CHECK (hours_per_week BETWEEN 0 AND 80),
    notes TEXT,
    FOREIGN KEY (job_id) REFERENCES JobPosting(job_id)
);

-- Blacklist
CREATE TABLE Blacklist (
    blacklist_id INT AUTO_INCREMENT PRIMARY KEY,
    employer_id INT NOT NULL,
    reason TEXT NOT NULL,
    date_added DATE DEFAULT CURRENT_DATE,
    added_by VARCHAR(100),
    FOREIGN KEY (employer_id) REFERENCES Employer(employer_id)
);
```
### 4. Load Sample Data

```sql
-- Employers
INSERT INTO Employer (name, blacklist_flag) VALUES
('Google', FALSE),
('Shopify', FALSE),
('StartupX', TRUE);

-- Job Postings
INSERT INTO JobPosting (employer_id, title, location, term) VALUES
(1, 'Software Engineer Intern', 'Waterloo, ON', 'Winter 2025'),
(2, 'Frontend Developer Intern', 'Toronto, ON', 'Fall 2025'),
(3, 'Data Analyst Intern', 'Remote', 'Spring 2025');

-- Salaries (salary info + benefits go here)
INSERT INTO Salary (job_id, hourly_rate, hours_per_week, notes) VALUES
(1, 45.00, 40, 'Free lunch + stock options'),
(2, 30.00, 37, 'Health + dental benefits'),
(3, 20.00, 35, 'No benefits, flagged as below average');

-- Blacklist (if any employer is flagged)
INSERT INTO Blacklist (employer_id, reason, added_by) VALUES
(3, 'Reported unfair treatment', 'Admin A');
```
---
### Contributors
<table> <tbody> <tr> <td align="center" valign="top" width="14.28%"> <a href="https://github.com/anddrewl"><img src="https://avatars.githubusercontent.com/u/136935667?v=4" width="100px;" alt="Andrew Lu"/><br /><sub><b>Andrew Lu</b></sub></a> </td> <td align="center" valign="top" width="14.28%"> <a href="https://github.com/bkctrl"><img src="https://avatars.githubusercontent.com/u/112859636?v=4" width="100px;" alt="BK Kang"/><br /><sub><b>BK Kang</b></sub></a> </td> <td align="center" valign="top" width="14.28%"> <a href="https://github.com/esleelg"><img src="https://avatars.githubusercontent.com/u/197958141?v=4" width="100px;" alt="Eunseo Lee"/><br /><sub><b>Eunseo Lee</b></sub></a> </td> <td align="center" valign="top" width="14.28%"> <a href="https://github.com/vncntchn05"><img src="https://avatars.githubusercontent.com/u/136762634?v=4" width="100px;" alt="Vincent Chen"/><br /><sub><b>Vincent Chen</b></sub></a> </td> </tr> </tbody> </table>

### License
This project is for educational purposes (CS348, University of Waterloo).
Dataset derived from Reddit self-reports, cleaned and transformed by our team.
