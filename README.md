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