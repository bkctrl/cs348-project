import pandas as pd
from sqlalchemy import create_engine
import re
from faker import Faker
import datetime

fake = Faker()
engine = create_engine('mysql+mysqlconnector://root:@localhost/coop_salaries')  # Adjusted based on app.py defaults

faculties = ['Engineering', 'Mathematics', 'Science', 'Arts', 'Business']
programs = {
  'Engineering': ['Computer Engineering', 'Software Engineering', 'Mechanical Engineering', 'Electrical Engineering'],
  'Mathematics': ['Computer Science', 'Pure Mathematics', 'Statistics', 'Actuarial Science'],
  'Science': ['Biology', 'Chemistry', 'Physics', 'Environmental Science'],
  'Arts': ['Psychology', 'English', 'History', 'Fine Arts'],
  'Business': ['Business Administration', 'Accounting', 'Finance', 'Marketing']
}

def parse_salary(s):
  if pd.isna(s): return None
  original = str(s)
  s = str(s).replace(',', '').lower()
  # Look for explicit /hr values, including approximated ones like ~$51/hr
  match = re.search(r'~\$?(\d+\.?\d*)/hr', s) or re.search(r'(\d+\.?\d*)/hr', s) or re.search(r'(\d+\.?\d*)\s*usd/hr', s)
  if match:
    num = float(match.group(1))
    if 'usd' in s: num *= 1.35  # Approximate USD to CAD conversion
    return round(num, 2)
  # For monthly values
  match = re.search(r'(\d+\.?\d*)\s*usd/month', s) or re.search(r'(\d+\.?\d*)/mo', s) or re.search(r'(\d+\.?\d*)/month', s)
  if match:
    num = float(match.group(1))
    if 'usd' in s: num *= 1.35
    return round(num / 160, 2)  # Assuming 40 hours/week * 4 weeks
  # For weekly values
  if 'week' in s or '/wk' in s:
    match = re.search(r'(\d+\.?\d*)', s)
    if match:
      num = float(match.group(1))
      if 'usd' in s: num *= 1.35
      return round(num / 40, 2)
  # For annual values, including k for thousands
  if 'annual' in s or 'yr' in s or 'k ' in s:
    match = re.search(r'(\d+\.?\d*)k?', s)
    if match:
      num = float(match.group(1))
      if 'k' in match.group(0): num *= 1000
      if 'usd' in s: num *= 1.35
      return round(num / 2080, 2)  # 40 hours/week * 52 weeks
  # For ranges like 20-25/hr
  match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)/hr', s)
  if match:
    return round((float(match.group(1)) + float(match.group(2))) / 2, 2)
  # Default: take the first number and assume /hr unless specified otherwise
  match = re.search(r'(\d+\.?\d*)', s)
  if match:
    num = float(match.group(1))
    if 'mo' in s or 'month' in s:
      num /= 160
    elif 'week' in s:
      num /= 40
    elif 'annual' in s or 'yr' in s:
      num /= 2080
    if 'usd' in s: num *= 1.35
    return round(num, 2)
  return None

def parse_stipend(s):
  if pd.isna(s): return None
  s = str(s).replace(',', '').lower()
  if 'unpaid' in s: return 0
  match = re.search(r'(\d+\.?\d*)', s)
  if match:
    num = float(match.group(1))
    if 'lump sum' in s: num /= 6  # Assume 6 months for lump sum
    num *= 0.016  # Approximate INR to CAD conversion
    return round(num, 2)
  return None

def process_waterloo(df):
  # Clean and parse
  df['Company / Role'] = df['Company / Role'].str.replace('⁠', '').str.strip()
  # Blacklist
  df['reason'] = None
  mask = df['Company / Role'].str.contains('(See Blacklist)', na=False)
  df.loc[mask, 'reason'] = 'Blacklisted'
  df['Company / Role'] = df['Company / Role'].str.replace('(See Blacklist)', '').str.strip()
  # Title
  def extract_title(row):
    if pd.notna(row['Position']): return row['Position']
    words = row['Company / Role'].split()
    if len(words) > 1 and any(keyword in words[-1].lower() for keyword in ['analyst', 'developer', 'engineer', 'intern', 'co-op', 'coop']):
      return ' '.join(words[1:])  # Assume first word is company, rest is role
    return 'Co-op Intern'
  df['title'] = df.apply(extract_title, axis=1)
  # Name
  def extract_name(row):
    return row['Company / Role'].replace(row['title'], '').strip()
  df['name'] = df.apply(extract_name, axis=1)
  # Hourly rate
  df['hourly_rate'] = df['Salary Information (CAD unless otherwise specified)'].apply(parse_salary)
  # Notes
  df['notes'] = df['Benefits'].fillna('') + ' ; Year: ' + df['Year'].fillna('')
  # Term
  df['term'] = df['Year'].apply(lambda y: f'Fall {y}' if pd.notna(y) else 'Fall 2024')
  # Location (default since not in CSV)
  df['location'] = 'Waterloo, ON'
  # Select relevant columns
  return df[['name', 'title', 'location', 'term', 'hourly_rate', 'notes', 'reason']]

def process_internship(df):
  # Title and name
  df['title'] = df['internship_title']
  df['name'] = df['company_name']
  df['location'] = df['location']
  # Term (default since start_date is 'Immediately')
  df['term'] = 'Winter 2026'
  # Monthly salary from stipend
  df['monthly_salary'] = df['stipend'].apply(parse_stipend)
  # Notes
  df['notes'] = df['start_date'] + ' for ' + df['duration']
  # No reason
  df['reason'] = None
  # Select relevant columns
  return df[['name', 'title', 'location', 'term', 'monthly_salary', 'notes', 'reason']]

def process_data(input_data):
  if isinstance(input_data, pd.DataFrame):
    df = input_data
    filename = 'unknown'
  else:
    filename = input_data
    skip = 1 if 'waterloo_coop.csv' in filename else 0
    df = pd.read_csv(input_data, skiprows=skip)
  
  # File-specific processing
  if 'waterloo_coop.csv' in filename:
    df = process_waterloo(df)
  elif 'internship.csv' in filename:
    df = process_internship(df)
  # Else, assume general
  
  # Standardize columns
  column_map = {
    'Company': 'name', 'Employer': 'name',
    'Role': 'title', 'Position': 'title', 'Job Title': 'title',
    'Location': 'location',
    'Term': 'term', 'Season': 'term', 'Year': 'term', 'Internship Term': 'term',
    'Salary': 'hourly_rate', 'Hourly Rate': 'hourly_rate', 'Monthly Stipend': 'monthly_salary',
    'Blacklist Reason': 'reason', 'Notes': 'notes', 'Benefits': 'notes'
  }
  df = df.rename(columns=column_map)
  
  # Convert monthly to hourly
  if 'monthly_salary' in df.columns:
    df['hourly_rate'] = df['monthly_salary'] / 160.0
    df = df.drop(columns=['monthly_salary'])
  
  # Clean hourly_rate if not already parsed
  if 'hourly_rate' in df.columns:
    df['hourly_rate'] = df['hourly_rate'].apply(lambda x: parse_salary(x) if pd.isna(x) or not isinstance(x, (int, float)) else x)
    df = df[df['hourly_rate'].notna() & (df['hourly_rate'] > 0)]
  
  # Defaults
  df['blacklist_flag'] = df.get('reason').notnull().astype(int)
  df['hours_per_week'] = 40
  df['term'] = df['term'].fillna(fake.random_element(['Fall 2025', 'Winter 2025', 'Spring 2026', 'Summer 2026']))
  df['location'] = df['location'].fillna(fake.city())
  df['notes'] = df['notes'].fillna('')
  
  # Employers
  df_employers = df[['name', 'blacklist_flag']].drop_duplicates()
  df_employers.to_sql('Employer', engine, if_exists='append', index=False)
  
  # Fetch employer IDs
  df_employers_loaded = pd.read_sql('SELECT employer_id, name FROM Employer', engine)
  df = df.merge(df_employers_loaded, on='name')
  
  # JobPostings
  df_jobs = df[['employer_id', 'title', 'location', 'term']].drop_duplicates()
  df_jobs.to_sql('JobPosting', engine, if_exists='append', index=False)
  
  # Fetch job IDs
  df_jobs_loaded = pd.read_sql('SELECT job_id, employer_id, title, location, term FROM JobPosting', engine)
  df = df.merge(df_jobs_loaded, on=['employer_id', 'title', 'location', 'term'])
  
  # Salaries (allow multiple per job)
  df_sal = df[['job_id', 'hourly_rate', 'hours_per_week', 'notes']].dropna(subset=['job_id'])
  df_sal.to_sql('Salary', engine, if_exists='append', index=False, method='multi')
  
  # Blacklists
  if 'reason' in df.columns:
    df_bl = df[df['reason'].notnull()][['employer_id', 'reason']].drop_duplicates()
    df_bl['date_added'] = datetime.date.today()
    df_bl['added_by'] = 'system'
    df_bl.to_sql('Blacklist', engine, if_exists='append', index=False)
  
  # Update blacklist flags
  with engine.connect() as conn:
    conn.execute("""
      UPDATE Employer e
      SET e.blacklist_flag = 1
      WHERE EXISTS (SELECT 1 FROM Blacklist b WHERE b.employer_id = e.employer_id);
    """)
  
  # Generate synthetic students and placements for each data row
  with engine.connect() as conn:
    for _, row in df.iterrows():
      if 'job_id' not in row or pd.isna(row['job_id']): continue
      job_id = int(row['job_id'])
      fac = fake.random_element(faculties)
      prog = fake.random_element(programs[fac])
      year = fake.random_int(1, 5)
      name = fake.name()
      # Insert student
      conn.execute(
        "INSERT INTO Student (name, faculty, program, year) VALUES (%s, %s, %s, %s)",
        (name, fac, prog, year)
      )
      student_id = conn.execute("SELECT LAST_INSERT_ID()").fetchone()[0]
      # Derive start/end dates from term
      term = row['term']
      year_match = re.search(r'(\d{4})', term)
      yr = int(year_match.group(1)) if year_match else 2025
      season = term.split()[0].lower() if ' ' in term else ''
      if season == 'winter':
        start_date = datetime.date(yr, 1, 1)
        end_date = datetime.date(yr, 4, 30)
      elif season in ['spring', 'summer']:
        start_date = datetime.date(yr, 5, 1)
        end_date = datetime.date(yr, 8, 31)
      elif season == 'fall':
        start_date = datetime.date(yr, 9, 1)
        end_date = datetime.date(yr, 12, 31)
      else:
        start_date = fake.date_between(start_date='-1y', end_date='+1y')
        end_date = fake.date_between_dates(date_start=start_date, date_end=start_date + datetime.timedelta(days=120))
      # Insert placement
      conn.execute(
        "INSERT INTO Placement (student_id, job_id, start_date, end_date) VALUES (%s, %s, %s, %s)",
        (student_id, job_id, start_date, end_date)
      )
  
  print(f'Processed {len(df)} rows. Tables populated: Employer, JobPosting, Salary, Blacklist, Student, Placement')

# Add more synthetic data if the dataset is small
def add_synthetic(n=5000):
  synth_data = []
  for _ in range(n):
    synth_data.append({
      'name': fake.company(),
      'title': fake.random_element(['Software Engineer Intern', 'Data Analyst Intern', 'Product Manager Intern']),
      'location': fake.city(),
      'term': fake.random_element(['Fall 2025', 'Winter 2025', 'Spring 2026', 'Summer 2026']),
      'hourly_rate': round(fake.random.uniform(20, 80), 2),
      'reason': fake.sentence() if fake.boolean(chance_of_getting_true=10) else None
    })
  synthetic_df = pd.DataFrame(synth_data)
  process_data(synthetic_df)

process_data('waterloo_coop.csv')
process_data('internship.csv')
add_synthetic()
