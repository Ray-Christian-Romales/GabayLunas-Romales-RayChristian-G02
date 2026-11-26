## Core Feature: Gabay Symptom Check & Reviewer Content Management
- **Gabay Symptom Check (Citizen):** Citizens select one or more symptoms to view up to five approved illnesses ranked by weighted match percentage, complete with URGENT red-flag emergency banners, ADVISORY notices, and automatic saved search history (view, delete single entry, and clear all).
- **Reviewer Content Management (Medical Reviewer):** Medical Reviewers manage symptoms (including red-flag warnings) and illnesses (with weighted symptom associations) through full CRUD operations, enforced by a dual-reviewer approval workflow (`PENDING` → `APPROVED`, preventing self-approval).

## Setup & Installation
1. Clone the repository and open the project folder:
   ```bash
   git clone https://github.com
   cd GabayLunas-Romales-RayChristian-G02
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your `SECRET_KEY`, `DEBUG`, and Supabase `DATABASE_URL`.
5. Run database migrations and start the development server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```


## Roles
- Citizen User: self-registers
- Medical Reviewer / Admin: created with `createsuperuser` or the shell


## Running Tests
Run the automated test suite (13 tests covering access control, validation, redirect-after-POST, custom 404, and approval rules):
```bash
python manage.py test
```
> **Supabase note:** Django's test runner creates a temporary test database (`test_postgres`), which requires a direct or session connection (port `5432`) in `.env` rather than the transaction pooler (port `6543`). If your Supabase role does not have `CREATEDB` permission, `settings.py` falls back to an in-memory SQLite database when running `test`.
