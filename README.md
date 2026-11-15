# GabayLunas

Symptom guide, OTC medicine guide and Cebu hospital directory (Django + Supabase PostgreSQL).

## Run locally
1. `python -m venv .venv` then `.venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your values
4. `python manage.py migrate`
5. `python manage.py createsuperuser` (becomes a Reviewer)
6. `python manage.py runserver 8001`

## Roles
- Citizen User: self-registers
- Medical Reviewer / Admin: created with `createsuperuser` or the shell