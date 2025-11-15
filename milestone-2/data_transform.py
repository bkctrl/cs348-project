# data_transform.py still needs modification and testing

import pandas as pd
from sqlalchemy import create_engine
import re
from faker import Faker

fake = Faker()
engine = create_engine('mysql+mysqlconnector://user:password@localhost/YOUR_DB')  # REPLACE

def process_csv(file_path):
    df = pd.read_csv(file_path)
    
    # standardize the columns
    column_map = {
        'Company': 'name', 'Employer': 'name',
        'Role': 'title', 'Position': 'title', 'Job Title': 'title',
        'Location': 'location',
        'Term': 'term', 'Season': 'term', 'Year': 'term', 'Internship Term': 'term',
        'Salary': 'hourly_rate', 'Hourly Rate': 'hourly_rate', 'Monthly Stipend': 'monthly_salary',
        'Blacklist Reason': 'reason', 'Notes': 'notes', 'Benefits': 'notes'
    }
    df = df.rename(columns=column_map)
    
    # convert monthly salary to hourly (assuming 40 hours/week and 4 weeks/month)
    if 'monthly_salary' in df.columns:
      df['hourly_rate'] = df['monthly_salary'] / 160.0
      df = df.drop(columns=['monthly_salary'])
    
    # clean hourly_rate values
    if 'hourly_rate' in df.columns:
      df['hourly_rate'] = df['hourly_rate'].astype(str).apply(lambda x: float(re.sub(r'[^0-9.]', '', x)) if re.sub(r'[^0-9.]', '', x) else None)
      df = df[df['hourly_rate'] > 0]
    
    # default values
    df['blacklist_flag'] = df.get('reason').notnull().astype(int)
    df['hours_per_week'] = 40
    df['term'] = df['term'].fillna(fake.random_element(['Fall 2025', 'Winter 2025', 'Spring 2026', 'Summer 2026']))
    df['location'] = df['location'].fillna(fake.city())
    df['notes'] = df['notes'].fillna('')
    
    # employers
    df_employers = df[['name', 'blacklist_flag']].drop_duplicates()
    df_employers.to_sql('Employer', engine, if_exists='append', index=False)
    
    # fetch employer IDs
    df_employers_loaded = pd.read_sql('SELECT employer_id, name FROM Employer', engine)
    df = df.merge(df_employers_loaded, on='name')
    
    # JobPostings
    df_jobs = df[['employer_id', 'title', 'location', 'term']].drop_duplicates()
    df_jobs.to_sql('JobPosting', engine, if_exists='append', index=False)
    
    # fetch job IDs
    df_jobs_loaded = pd.read_sql('SELECT job_id, employer_id, title, location, term FROM JobPosting', engine)
    df = df.merge(df_jobs_loaded, on=['employer_id', 'title', 'location', 'term'])
    
    # salaries
    df_sal = df[['job_id', 'hourly_rate', 'hours_per_week', 'notes']].dropna(subset=['job_id'])
    df_sal = df_sal.drop_duplicates(subset=['job_id'])
    df_sal.to_sql('Salary', engine, if_exists='append', index=False, method='multi')
    
    # blacklists
    if 'reason' in df.columns:
      df_bl = df[df['reason'].notnull()][['employer_id', 'reason']].drop_duplicates()
      df_bl['date_added'] = '2025-11-14'
      df_bl.to_sql('Blacklist', engine, if_exists='append', index=False)
    
    # update blacklist flags
    with engine.connect() as conn:
      conn.execute("""
        UPDATE Employer e
        SET e.blacklist_flag = 1
        WHERE EXISTS (SELECT 1 FROM Blacklist b WHERE b.employer_id = e.employer_id);
      """)
    
    print(f'Processed {len(df)}. Total tuples added: {len(df) * 4}')

# Example usage (run for each source CSV)
# process_csv('waterloo_coop.csv', 'Waterloo Co-op')
# process_csv('internship.csv', 'Kaggle')
# process_csv('levels_fyi.csv', 'levels.fyi')
# process_csv('scoper.csv', 'scoper.fyi') if data exists

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
  process_csv(synthetic_df)

# add_synthetic()
