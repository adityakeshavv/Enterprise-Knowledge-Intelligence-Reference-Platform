# Nebula9 frontend

The frontend is a React and TypeScript workspace for asking questions, reviewing sourced answers, exploring execution traces, and selecting industry packs.

## Run locally

```powershell
cd frontend
npm install
npm run dev
```

The API defaults to `http://localhost:8000/api`. To use another backend, add a `frontend/.env.local` file:

```text
VITE_API_BASE_URL=http://localhost:8000/api
```

Sign-in uses the backend `/auth/login` endpoint. The Home page's scenario catalog opens a preview before submitting. Knowledge Sources is currently a representative demo catalog, and Session & Governance shows the current browser session rather than a persistent audit ledger.
