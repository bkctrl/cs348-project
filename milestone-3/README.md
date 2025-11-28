<h1 align="center">Waterloo Co-op Salaries Explorer</h1>

<p align="center">
  Milestone 3: Final Project <br />
  November 27, 2025
</p>

<p align="center">
  <a href="#"><img alt="Status" src="https://img.shields.io/badge/status-M3_ready-4CAF50.svg"></a>
  <a href="#"><img alt="Database" src="https://img.shields.io/badge/db-MySQL_8+-blue.svg"></a>
  <a href="#"><img alt="API" src="https://img.shields.io/badge/api-Flask-ff6f61.svg"></a>
</p>

---

## 🧱 Project Setup

#### 1. Navigate to Project Directory
```bash
cd milestone-3
```

#### 1.1 Set Environment Variables
Create a `.env` file. For testing purposes, you could have:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASS=password
DB_NAME=coop_salaries
```

#### 2. Start MySQL Database with Docker
```bash
# Start the MySQL container
docker pull mysql:8.0
docker-compose up -d

# Verify the container is running
docker ps
```

Feel free to modify `docker-compose.yml` as appropriate!

#### 3. Create Database Schema
```
# Load the table definitions
docker exec -i coop_salaries_db mysql -uroot -ppassword coop_salaries < create-tables.sql
```

#### 4. Set Up Python Environment
```bash
# Install Python dependencies
pip3 install pandas sqlalchemy mysql-connector-python faker
```

#### 5. Load Data
```bash
# Run the data transformation script
python3 data_transform.py
```

#### 6. Install Flask Application Dependencies
```bash
cd app
pip3 install flask mysql-connector-python
```

#### 7. Run the Flask Application
```bash
python3 app.py
```
Application will start on: http://127.0.0.1:5000

#### API Endpoints:

Add Employer to Blacklist
```bash
curl -X POST http://127.0.0.1:5000/admin/blacklist-add \
  -d "employer_id=6" \
  -d "reason=Failed to pay interns"
```

Remove Employer from Blacklist
```bash
curl -X POST http://127.0.0.1:5000/admin/blacklist-remove \
  -d "employer_id=6"
```

## 📌 Implemented Features (`app/app.py`)

### Basic Features (R6-R10)
#### 1. Keyword Search (R6)

Route: `/search`

Description: Search job postings by title, employer, or location using partial matches.

#### 2. Top-Paying Companies by Given Role (R7)

Route: `/top-companies`

Description: User selects a job role and views top 20 employers ranked by average hourly rate.

#### 3. Average Salary by Faculty / Program (R8)

Route: `/avg-salary`

Description: Displays average hourly salaries grouped by faculty and program, with optional filters for faculty, program keyword, and term.

#### 4. Average Salary by Term (R9)

Route: `/avg-by-term`

Description: Aggregates salary by academic term, showing average hourly wage and number of reports.

#### 5. View Blacklisted Employers (R10)

Route: `/blacklist`

Description: Displays employers flagged as blacklisted, including reason and date added.


### Advanced Features (R11-R15)
#### 6. Full-Text Relevance Search (R11)

**Route:** `/advanced-search`  
**Description:** Provides an “advanced search” interface that searches titles, locations, and employer names using a single keyword and returns matching jobs ordered by hourly rate. (Implemented with `LIKE` for compatibility, but designed as an advanced search feature.)

#### 7. Add & Remove Blacklist Entry (Transactional) (R12)

**Route:** `/admin/blacklist-add`, `/admin/blacklist-remove`
**Description:** Admin-only feature that inserts a blacklist record and updates the employer’s blacklist flag inside a single transaction, with rollback on failure to maintain consistency.

#### 8. Safe Employer Recommendations by Faculty (R13)

**Route:** `/safe-employers`  
**Description:** Recommends “safe” employers for a given faculty by combining Placement, Student, Salary, JobPosting, and Employer data to:
- Exclude blacklisted employers  
- Require a minimum number of placements  
- Exclude employers with salaries significantly below the faculty average  
Results are sorted by average hourly rate and number of placements.

#### 9. Auto-Flagging Low-Paying Employers (R14)

**Route:** `/admin/add-salary`  
**Description:** Admin endpoint for inserting or updating salary reports (via `INSERT ... ON DUPLICATE KEY UPDATE`) as part of an auto-flagging workflow for low-paying employers.

#### 10. Salary Percentiles & Bands (R15)

**Route:** `/salary-bands`  
**Description:** Computes salary percentile ranks and decile bands for jobs filtered by title, city, and term, using MySQL window functions (`PERCENT_RANK`, `NTILE(10)`). Shows where each job’s pay sits in the distribution (e.g., bottom 20%, median, top 10%).


