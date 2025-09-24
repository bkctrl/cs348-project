<h1 align="center">UWaterloo Reddit-Powered Company Insights</h1>

<p align="center">
  Crowd-sourced insights on <b>pay ranges</b>, <b>benefits</b>, <b>interview experience</b>, and <b>blacklist flags</b> for companies recruiting UW students — mined from r/uwaterloo & related subreddits.
</p>

<p align="center">
  <a href="#"><img alt="Status" src="https://img.shields.io/badge/status-M0_ready-4CAF50.svg"></a>
  <a href="#"><img alt="Database" src="https://img.shields.io/badge/db-MySQL_8+-blue.svg"></a>
  <a href="#"><img alt="API" src="https://img.shields.io/badge/api-Flask-ff6f61.svg"></a>
</p>

---

## ✨ Overview
This project ingests public Reddit discussions about **co-op/intern experiences** for **University of Waterloo** students and turns them into a clean, queryable **database**.  
Initial scope (M0): read-only demo with a toy dataset and 2–3 API routes.  
Later milestones: robust scraping, de-duplication, pay band normalization, quality scoring, dashboards.

---

## 🚀 Features
- **Company directory** with **pay reports** (range, currency, period), **benefits** (health, WFH, relocation, housing), and **flags** (ghosting, rescinded offers, toxicity).
- **Source tracing** back to the **post/comment** (stored as URL + anonymized ID).
- **Search & filter** by term, company, term type (Intern/Co-op), location, sector.
- **Quality signals** (planned): confidence score from upvotes, comment corroboration, and author karma.

**M0 (this week)**  
- MySQL schema + seed  
- Hello-world API (list/filter/lookup)  
- Sample SQL tests + expected output

---
## ⚙️ Setup

SSH into the general-use host:

```bash
ssh <your_user>@ubuntu2204-004.student.cs.uwaterloo.ca
```

Then clone the repo:

```bash
git clone git@github.com:bkctrl/cs348-project.git
cd cs348-project/milestone-0
```

If SSH fails, use HTTPS instead:

```bash
git clone https://github.com/bkctrl/cs348-project.git
```

Now run the `setup.sh` script:
```bash
chmod +x setup.sh && ./setup.sh
```

Verify the database:
```bash
mysql -u default-user -p -e "SHOW DATABASES;"
```
---


