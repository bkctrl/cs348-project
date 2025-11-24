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

# Feature: Top-Paying Companies by Given Role (R7)
@app.route("/top-companies", methods=["GET", "POST"])
def top_companies():
  db = get_db()
  cur = db.cursor(dictionary=True)

  role = request.form.get("role") if request.method == "POST" else None

  if role:
    cur.execute("""
      SELECT e.name AS company,
             ROUND(AVG(s.hourly_rate), 2) AS avg_hourly,
             COUNT(*) AS n_reports
      FROM Employer e
      JOIN JobPosting j ON j.employer_id = e.employer_id
      JOIN Salary     s ON s.job_id       = j.job_id
      WHERE j.title = %s
      GROUP BY e.name
      ORDER BY avg_hourly DESC, n_reports DESC
      LIMIT 20;
    """, (role,))
    rows = cur.fetchall()
    cur.close(); db.close()
    return render_template("top_companies.html", rows=rows, role=role)
  else:
    cur.execute("SELECT DISTINCT title FROM JobPosting ORDER BY title;")
    roles = [row["title"] for row in cur.fetchall()]
    cur.close(); db.close()
    return render_template("select_role.html", roles=roles)

# Feature: Average Salary by Faculty / Program (R8)
@app.get("/avg-salary")
def avg_salary():
    fac = request.args.get("faculty", "").strip()
    prog = request.args.get("program_kw", "").strip()
    term = request.args.get("term", "").strip()

    fac_like = f"%{fac}%" if fac else "%"
    prog_like = f"%{prog}%" if prog else "%"
    term_like = f"%{term}%" if term else "%"

    db = get_db()
    cur = db.cursor()

    cur.execute("""
      SELECT s.faculty,
             s.program,
             ROUND(AVG(sa.hourly_rate), 2) AS avg_hourly_rate,
             COUNT(*) AS n_placements
      FROM Placement p
      JOIN Student s ON p.student_id = s.student_id
      JOIN Salary sa ON p.job_id = sa.job_id
      JOIN JobPosting j ON p.job_id = j.job_id
      WHERE s.faculty LIKE %s
        AND s.program LIKE %s
        AND j.term LIKE %s
      GROUP BY s.faculty, s.program
      ORDER BY avg_hourly_rate DESC, n_placements DESC
    """, (fac_like, prog_like, term_like))

    rows = [
      {
        "faculty": r[0],
        "program": r[1],
        "avg_hourly_rate": float(r[2]),
        "n_placements": int(r[3])
      }
      for r in cur.fetchall()
    ]

    cur.close(); db.close()

    return render_template("avg_salary.html", rows=rows, faculty=fac, program_kw=prog, term=term)

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

# Feature: View Blacklisted Employers (R10)
@app.get("/blacklist")
def view_blacklist():
  db = get_db(); cur = db.cursor()
  cur.execute("""
      SELECT e.name AS employer_name,
            b.reason,
            b.date_added
      FROM Employer e
      JOIN Blacklist b ON e.employer_id = b.employer_id
      WHERE e.blacklist_flag = TRUE
      ORDER BY b.date_added DESC, e.name
  """)
  # Map tuple results to dictionaries, matching the style of the other routes
  rows = [{"employer_name": r[0], "reason": r[1], "date_added": r[2]} for r in cur.fetchall()]
  cur.close(); db.close()
  return render_template("blacklist.html", reports=rows)

# Feature: Full-Text Relevance Search (R11)
@app.get("/advanced-search")
def advanced_search():
    keyword = request.args.get("q", "")
    if not keyword:
        return render_template("search_results.html", jobs=[])
    
    db = get_db()
    cur = db.cursor()
    
    # Simplified query with proper FULLTEXT usage
    cur.execute("""
        SELECT DISTINCT j.title, 
               e.name AS employer, 
               j.location, 
               s.hourly_rate,
               (
                 CASE 
                   WHEN MATCH(j.title) AGAINST(%s IN NATURAL LANGUAGE MODE) > 0 
                   THEN MATCH(j.title) AGAINST(%s IN NATURAL LANGUAGE MODE) * 2.0
                   ELSE 0
                 END +
                 CASE 
                   WHEN MATCH(j.location) AGAINST(%s IN NATURAL LANGUAGE MODE) > 0 
                   THEN MATCH(j.location) AGAINST(%s IN NATURAL LANGUAGE MODE)
                   ELSE 0
                 END +
                 CASE 
                   WHEN MATCH(e.name) AGAINST(%s IN NATURAL LANGUAGE MODE) > 0 
                   THEN MATCH(e.name) AGAINST(%s IN NATURAL LANGUAGE MODE)
                   ELSE 0
                 END
               ) AS relevance_score
        FROM JobPosting j
        JOIN Employer e ON j.employer_id = e.employer_id
        JOIN Salary s ON j.job_id = s.job_id
        WHERE MATCH(j.title) AGAINST(%s IN NATURAL LANGUAGE MODE)
           OR MATCH(j.location) AGAINST(%s IN NATURAL LANGUAGE MODE)
           OR MATCH(e.name) AGAINST(%s IN NATURAL LANGUAGE MODE)
        HAVING relevance_score > 0
        ORDER BY relevance_score DESC, s.hourly_rate DESC
    """, (keyword, keyword, keyword, keyword, keyword, keyword, keyword, keyword, keyword))
    
    rows = [{"title": r[0], "employer": r[1], "location": r[2], "hourly_rate": r[3]} 
            for r in cur.fetchall()]
    
    cur.close()
    db.close()
    
    return render_template("search_results.html", jobs=rows)


# Feature: Add Blacklist Entry (Transactional) (R12)
@app.post("/admin/blacklist-add")
def add_blacklist_entry():
    employer_id = request.form.get("employer_id")
    reason = request.form.get("reason")
    admin_user = "admin@system.com"  # From session in production
    
    db = get_db(); cur = db.cursor()
    try:
        db.start_transaction()
        
        # Insert blacklist record
        cur.execute("""
            INSERT INTO Blacklist (employer_id, reason, date_added, added_by)
            VALUES (%s, %s, CURDATE(), %s)
        """, (employer_id, reason, admin_user))
        
        # Update employer flag
        cur.execute("""
            UPDATE Employer SET blacklist_flag = TRUE
            WHERE employer_id = %s
        """, (employer_id,))
        
        db.commit()
        return "Employer blacklisted successfully.", 200
    except Exception as err:
        db.rollback()
        return f"Error: Could not add blacklist entry. Data has been rolled back.", 500
    finally:
        cur.close(); db.close()

# Feature: Salary Percentiles and Bands (R15)
@app.get("/salary-bands")
def salary_bands():
  title = (request.args.get("title", "") or "").strip()
  city  = (request.args.get("city", "") or "").strip()
  term  = (request.args.get("term", "") or "").strip()

  filters, params = [], []

  if title:
    filters.append("j.title = %s")
    params.append(title)

  if city:
    filters.append("j.location = %s")
    params.append(city)

  if term:
    filters.append("j.term = %s")
    params.append(term)

  where_clause = " AND ".join(filters) if filters else "1=1"

  query = f"""
    WITH filtered AS (
      SELECT
        j.title,
        j.location,
        j.term,
        e.name AS employer,
        s.hourly_rate
      FROM JobPosting j
      JOIN Employer e ON j.employer_id = e.employer_id
      JOIN Salary   s ON j.job_id      = s.job_id
      WHERE {where_clause}
        AND s.hourly_rate IS NOT NULL
    ),
    ranked AS (
      SELECT
        employer,
        title,
        location,
        term,
        hourly_rate,
        PERCENT_RANK() OVER (
          PARTITION BY title, location, term
          ORDER BY hourly_rate
        ) AS pct_rank,
        NTILE(10) OVER (
          PARTITION BY title, location, term
          ORDER BY hourly_rate
        ) AS decile
      FROM filtered
    )
    SELECT
      employer,
      title,
      location,
      term,
      hourly_rate,
      ROUND(pct_rank, 2) AS pct_rank,
      decile
    FROM ranked
    ORDER BY hourly_rate;
  """

  db = get_db()
  cur = db.cursor(dictionary=True)
  cur.execute(query, params)
  rows = cur.fetchall()
  cur.close(); db.close()

  return render_template(
    "salary_bands.html",
    rows=rows,
    title=title,
    city=city,
    term=term,
  )

if __name__ == "__main__":
  app.run(debug=True)
