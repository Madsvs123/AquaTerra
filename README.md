# AquaTerra

Smart irrigation monitoring and control for farms, greenhouses, and landscaping operators. Each organization manages its own sites, zones, devices, schedules, recommendations, alerts, and maintenance, with soil moisture, flow, and weather in one workspace.

## Stack

Django 5 and Django REST Framework, with JWT auth, Celery, and Django Channels. React 18, TypeScript, and Vite on the frontend. PostgreSQL and Redis.

## Layout

- `backend/` — Django API
- `frontend/` — React client

## Local setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Use PostgreSQL and Redis when the project expects them. Copy `.env.example` to `.env` where an example file is present, and keep real secrets out of git.

## License

Released under the [MIT License](LICENSE).
