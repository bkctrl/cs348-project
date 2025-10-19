from flask import Flask, render_template, request
import mysql.connector as mysql
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
  return mysql.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "coop_salaries"),
    auth_plugin="mysql_native_password"
)

app = Flask(__name__)

@app.get("/")
def index():
  return render_template("index.html")

# Employers with blacklist_flag
@app.get("/employers")
def employers():
  db = get_db(); cur = db.cursor()
  cur.execute("""
    SELECT employer_id, name, blacklist_flag
    FROM Employer
    ORDER BY employer_id
  """)
  rows = [{"employer_id": r[0], "name": r[1], "blacklist_flag": int(r[2])} for r in cur.fetchall()]
  cur.close(); db.close()
  return render_template("employers.html", rows=rows)

# Jobs with salary info (ordered by $ desc)
@app.get("/salaries")
def salaries():
  db = get_db(); cur = db.cursor()
  cur.execute("""
    SELECT e.name, j.title, s.hourly_rate
    FROM Employer e
    JOIN JobPosting j ON e.employer_id = j.employer_id
    JOIN Salary s ON j.job_id = s.job_id
    ORDER BY s.hourly_rate DESC
  """)
  rows = [{"name": r[0], "title": r[1], "hourly_rate": float(r[2])} for r in cur.fetchall()]
  cur.close(); db.close()
  return render_template("salaries.html", rows=rows)

# Companies paying below threshold (default $18)
@app.get("/low-wage")
def low_wage():
  try:
    threshold = float(request.args.get("threshold", "18"))
  except ValueError:
    threshold = 18.0

  db = get_db(); cur = db.cursor()
  cur.execute("""
    SELECT e.name, s.hourly_rate
    FROM Employer e
    JOIN JobPosting j ON e.employer_id = j.employer_id
    JOIN Salary s ON j.job_id = s.job_id
    WHERE s.hourly_rate < %s
    ORDER BY s.hourly_rate
  """, (threshold,))
  rows = [{"name": r[0], "hourly_rate": float(r[1])} for r in cur.fetchall()]
  cur.close(); db.close()
  return render_template("low_wage.html", rows=rows, threshold=threshold)

# Average Salary by Job Title
@app.get("/avg-by-title")
def avg_by_title():
  kw = (request.args.get("title_kw", "") or "").strip()
  like = f"%{kw}%" if kw else "%"
  db = get_db(); cur = db.cursor()
  cur.execute("""
    SELECT j.title,
           ROUND(AVG(s.hourly_rate), 2) AS avg_hourly,
           COUNT(*) AS n_reports
    FROM JobPosting j
    JOIN Salary s ON s.job_id = j.job_id
    WHERE j.title LIKE %s
    GROUP BY j.title
    ORDER BY avg_hourly DESC, n_reports DESC, j.title
  """, (like,))
  rows = [{"title": r[0], "avg_hourly": float(r[1]), "n_reports": int(r[2])} for r in cur.fetchall()]
  cur.close(); db.close()
  return render_template("avg_by_title.html", rows=rows, title_kw=kw)

# Feature: Keyword Search (R6)
@app.get("/search")
def search():
  keyword = (request.args.get("q", "") or "").strip()
  db = get_db(); cur = db.cursor()
  like = f"%{keyword}%"
  cur.execute("""
    SELECT j.title, e.name AS employer, j.location, j.term, s.hourly_rate
    FROM JobPosting j
    JOIN Employer  e ON j.employer_id = e.employer_id
    JOIN Salary    s ON j.job_id       = s.job_id
    WHERE %s = '' OR j.title LIKE %s OR e.name LIKE %s OR j.location LIKE %s
    ORDER BY s.hourly_rate DESC, j.title
  """, (keyword, like, like, like))
  rows = [{"title": r[0], "employer": r[1], "location": r[2], "term": r[3], "hourly_rate": float(r[4])} for r in cur.fetchall()]
  cur.close(); db.close()
  return render_template("search.html", q=keyword, rows=rows)

# Feature: Average Salary by Term (R9)
@app.get("/avg-by-term")
def avg_by_term():
  db = get_db(); cur = db.cursor()
  cur.execute("""
    SELECT j.term,
           ROUND(AVG(s.hourly_rate), 2) AS avg_hourly,
           COUNT(*) AS n_reports
    FROM JobPosting j
    JOIN Salary s ON s.job_id = j.job_id
    GROUP BY j.term
    ORDER BY j.term
  """)
  rows = [{"term": r[0], "avg_hourly": float(r[1]), "n_reports": int(r[2])} for r in cur.fetchall()]
  cur.close(); db.close()
  return render_template("avg_by_term.html", rows=rows)

if __name__ == "__main__":
  app.run(debug=True)
