<h1 align="center">Waterloo Co-op Salaries Explorer</h1>

<p align="center">
  Milestone 2: Proposal <br />
  November 14, 2025
</p>

<p align="center">
  <a href="#"><img alt="Status" src="https://img.shields.io/badge/status-M2_ready-4CAF50.svg"></a>
  <a href="#"><img alt="Database" src="https://img.shields.io/badge/db-MySQL_8+-blue.svg"></a>
  <a href="#"><img alt="API" src="https://img.shields.io/badge/api-Flask-ff6f61.svg"></a>
</p>

---

## 🧱 Create and Load the Sample Database

Create database and schema:
```bash
mysql -u root -p < milestone-1/create-tables.sql
```

Insert sample data and verify (test dataset from C3):
```bash
mysql -u root -p < milestone-1/test-sample.sql
```

You can confirm correct population by:

```bash
mysql -u root -p coop_salaries -e "SELECT * FROM Employer;"
```

## 📌 Implemented Features (`app/app.py`)

#### 1. Keyword Search (R6)

Route: `/search`

Description: Search job postings by title, employer, or location using partial matches.

#### 2. Average Salary by Faculty / Program (R8)

Route: `/avg-salary`

Description: Displays average hourly salaries grouped by faculty and program, with optional filters for faculty, program keyword, and term.

#### 3. Average Salary by Term (R9)

Route: `/avg-by-term`

Description: Aggregates salary by academic term, showing average hourly wage and number of reports.

#### 4. View Blacklisted Employers (R10)

Route: `/blacklist`

Description: Displays employers flagged as blacklisted, including reason and date added.

#### 5. Top-Paying Companies by Given Role (R7)

Route: `/top-companies`

Description: User selects a job role and views top 20 employers ranked by average hourly rate.

### 🔍 Additional Implemented Features
#### 6. Employers with Blacklist Flag

Route: `/employers`

#### 7. Jobs with Salary Info (All Reports)

Route: `/salaries`

#### 8. Companies Paying Below Threshold

Route: `/low-wage`

#### 9. Average Salary by Job Title

Route: `/avg-by-title`


## 🚀 Run the Application
Set up virtual environment:
```bash
cd milestone-1/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then edit your environment file (`.env`):

```bash
DB_HOST=127.0.0.1
DB_USER=
DB_PASS=
DB_NAME=coop_salaries
FLASK_ENV=development
```

Run the Flask app:
```bash
python3 app.py
```

Visit http://127.0.0.1:5000. 


#### Home Screen
<img width="1411" height="553" alt="Screenshot 2025-10-19 at 3 56 12 AM" src="https://github.com/user-attachments/assets/cf96d8e4-cf3d-49f9-8f06-8349146088ef" />


#### Employers with `blacklist_flag`
<img width="1382" height="491" alt="Screenshot 2025-10-19 at 3 56 28 AM" src="https://github.com/user-attachments/assets/07fe6eb0-9a8d-4325-b1fc-c04fa7d1b087" />


#### Jobs with salary info (ordered by $ desc)
<img width="1461" height="548" alt="Screenshot 2025-10-19 at 3 56 39 AM" src="https://github.com/user-attachments/assets/9a136222-199b-4319-90a7-b3d21dbcef1e" />


#### Companies paying below threshold (default $18)
<img width="1468" height="540" alt="Screenshot 2025-10-19 at 3 56 50 AM" src="https://github.com/user-attachments/assets/308c16ab-64fa-401d-b345-7f1392f2e62e" />

#### Average Salary by Job Title
<img width="1440" height="599" alt="Screenshot 2025-10-19 at 3 57 05 AM" src="https://github.com/user-attachments/assets/6675ae69-9520-451f-bb68-0f398b8c381f" />


#### Feature: Keyword Search (R6)
<img width="1451" height="597" alt="Screenshot 2025-10-19 at 3 57 29 AM" src="https://github.com/user-attachments/assets/1b33dbc9-5f2f-496f-9d76-53dc0bfe21f2" />


#### Feature: Average Salary by Term (R9)
<img width="1477" height="472" alt="Screenshot 2025-10-19 at 3 57 16 AM" src="https://github.com/user-attachments/assets/0f1bc9ec-50f0-465f-92dc-1fea2902c4fe" />





